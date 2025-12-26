import time
from typing import Any, Dict, Tuple


class TTLCache:
    def __init__(self, ttl_seconds: int = 60):
        self.ttl = ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str):
        entry = self._store.get(key)
        if not entry:
            return None

        expires_at, value = entry
        if time.time() > expires_at:
            # expired
            del self._store[key]
            return None

        return value

    def set(self, key: str, value: Any):
        expires_at = time.time() + self.ttl
        self._store[key] = (expires_at, value)
