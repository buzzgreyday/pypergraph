import threading

class SIDManager:
    def __init__(self):
        self._sid = 0
        self._lock = threading.Lock()

    def next_sid(self, prefix: str) -> str:
        with self._lock:
            self._sid += 1
            return f"{prefix}{self._sid}"

    def reset_sid(self):
        with self._lock:
            self._sid = 0

# Create a global instance
sid_manager = SIDManager()