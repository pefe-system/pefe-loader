from threading import Lock
import time
from ..config import *
import json

class ErrorReporter:
    def __init__(self, auto_flush=True):
        self._lock = Lock()
        self._auto_flush = auto_flush
        # Open once, keep open
        self._file = open(config["self"]["error_log_file"], 'a', encoding='utf-8')

    def log(self, agent_identity, content, err):
        """Log a message with the agent's identity."""
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with self._lock:
            self._file.write(f"{ts}: [{agent_identity}] | content: {json.dumps(content)} | error: {err}\n")
            if self._auto_flush:
                self._file.flush()

    def close(self):
        """Close the log file explicitly."""
        with self._lock:
            if self._file and not self._file.closed:
                self._file.close()

    def __del__(self):
        # Defensive cleanup in case close() wasn't called
        try:
            self.close()
        except Exception:
            pass
