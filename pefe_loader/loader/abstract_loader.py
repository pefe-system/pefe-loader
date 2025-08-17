class AbstractLoader:
    def __init__(self, get_next_content):
        self._get_next_content = get_next_content
    
    def get_next_content(self):
        return self._get_next_content()

    def register_consumer(self):
        raise NotImplementedError
    
    def run(self):
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError
    
    def consume(self, consumer_id):
        """
        If calling consume() yields StopIteration,
        you must not call consume_done() afterwards.
        """
        raise NotImplementedError
    
    def consume_done(self, consumer_id):
        raise NotImplementedError
