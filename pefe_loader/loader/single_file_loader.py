from .abstract_loader import AbstractLoader
import threading

class SingleFileLoader(AbstractLoader):
    """
    Load a single file and distribute it to all clients at a time.
    Wait for all clients to finish (either succeed or fail after
    MAX_RETRIES) then proceed to the next file.

    While this could be suitable in case of running multiple
    different feature extractors, it will be very slow when
    there are few.
    """
    def __init__(self, get_next_content):
        super().__init__(get_next_content)
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._consumed_set = set()
        self._client_count = 0
        self._last_content = None
        self._stop_event = threading.Event()
        self._thread = None

    def register_consumer(self):
        with self._lock:
            consumer_id = self._client_count
            self._client_count += 1
            return consumer_id
    
    def run(self):
        self._thread = threading.Thread(target=self._run_thread, daemon=False)
        self._thread.start()
        print("Loader started")
        self._thread.join()
    
    def stop(self):
        with self._cond:
            self._stop_event.set()
            self._cond.notify_all()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _run_thread(self):
        while not self._stop_event.is_set():
            try:
                new_content = self.get_next_content()
            except StopIteration:
                self._stop_event.set()
                with self._cond:
                    self._cond.notify_all()
                break

            with self._cond:
                self._last_content = new_content
                self._consumed_set.clear()
                self._cond.notify_all()  # wake up consumers

                # Wait until all consumers have processed it
                while len(self._consumed_set) < self._client_count and not self._stop_event.is_set():
                    self._cond.wait()

    def consume(self, consumer_id):
        with self._cond:
            while (self._last_content is None or consumer_id in self._consumed_set) and not self._stop_event.is_set():
                self._cond.wait()

            if self._stop_event.is_set():
                raise StopIteration

            return self._last_content

    def consume_done(self, consumer_id):
        with self._cond:
            self._consumed_set.add(consumer_id)
            if len(self._consumed_set) == self._client_count:
                self._cond.notify_all()
