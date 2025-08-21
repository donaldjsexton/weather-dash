import time
from typing import Any, Optional, Tuple

_store: dict[str, Tuple[float, Any]] = {}

def cache_get(key: str) -> Optional[Any]:
    item = _store.get(key)
    if not item:
        return None
    expires_at, value = item
    if time.time() > expires_at:
        _store.pop(key, None)
        return None
    return value

def cache_set(key: str, value: Any, ttl: int) -> None:
    _store[key] = (time.time() + ttl, value)

