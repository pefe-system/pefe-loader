from .abstract_loader import AbstractLoader
import threading

class SpreadFileLoader(AbstractLoader):
    """
    Load multiple files and spread them to multiple
    agents at once; no two agents would get the same
    file. This is not suitable in case of running
    feature extractors of different kinds (since
    each extractor gets their own different set
    of files). However, this would be extremely
    helpful when running multiple feature extractors
    of the same kind, where, eventually, all
    the engineered features get written to the
    same LMDB, while reducing overall processing
    time thanks to multithreading.
    """
    def __init__(self, get_next_content):
        super().__init__(get_next_content)
        self._lock = threading.Lock()
        self._client_count = 0
        self._start_event = threading.Event()
        self._stop_event = threading.Event()
        self._thread = None
        self._consume_done_cond = threading.Condition(self._lock)
        self._consuming_count = 0
        self._get_next_content_lock = threading.Lock()

    def register_consumer(self):
        with self._lock:
            id = self._client_count
            self._client_count += 1
            return id
    
    def run(self):
        self._thread = threading.Thread(target=self._run_thread, daemon=False)
        self._thread.start()
        self._start_event.set()
        print("Loader started")
        self._thread.join()

    def stop(self):
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _run_thread(self):
        self._stop_event.wait()
        # Wait for all consumer to gracefully finish
        with self._consume_done_cond:
            while self._consuming_count > 0:
                self._consume_done_cond.wait()

    def consume(self, consumer_id):
        try:
            self._start_event.wait()
            with self._consume_done_cond:
                self._consuming_count += 1
                self._consume_done_cond.notify_all()
            
            try:
                if self._stop_event.is_set():
                    raise StopIteration
                try:
                    with self._get_next_content_lock:
                        new_content = self.get_next_content()
                except StopIteration:
                    self._stop_event.set()
                    raise

                print(f"NEW CONTENT FOR CONSUMER {consumer_id}: {new_content}")
                return new_content
            except StopIteration:
                with self._consume_done_cond:
                    self._consuming_count -= 1
                    self._consume_done_cond.notify_all()
                raise
        except StopIteration:
            raise
        except Exception as e:
            print(f"EXCEPTION IN THREAD OF CONSUMER {consumer_id}: {e}")
            raise
    
    def consume_done(self, consumer_id):
        self._start_event.wait()
        with self._consume_done_cond:
            self._consuming_count -= 1
            self._consume_done_cond.notify_all()
