"""Cache for device connection state.

Persists the miIO protocol message sequence counter between CLI invocations.
Without this, restarting the CLI resets the counter to 0, and devices ignore
messages with sequence IDs they've already seen, causing timeouts.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import TypedDict

from platformdirs import user_cache_dir

_LOGGER = logging.getLogger(__name__)

CACHE_DIR = Path(user_cache_dir("python-miio"))


class DeviceState(TypedDict):
    """Cached state for a single device.

    seq: The miIO protocol message sequence counter. Each message sent to a
    device increments this counter, and the device tracks seen IDs to
    deduplicate. Persisting it avoids ID reuse across CLI invocations.
    """

    seq: int


def _cache_path(ip: str) -> Path:
    """Return the cache file path for a device IP.

    Uses a hash of the IP to avoid filesystem issues with IPv6 colons.
    """
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{ip_hash}.json"


def read_cache(ip: str) -> DeviceState:
    """Read cached connection state for a device."""
    path = _cache_path(ip)
    try:
        data = json.loads(path.read_text())
        seq = int(data["seq"])
        _LOGGER.debug("Loaded cache for %s: seq=%d", ip, seq)
        return DeviceState(seq=seq)
    except FileNotFoundError:
        return DeviceState(seq=0)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as ex:
        _LOGGER.warning("Corrupt cache for %s, ignoring: %s", ip, ex)
        return DeviceState(seq=0)


def write_cache(ip: str, state: DeviceState) -> None:
    """Write connection state to cache for a device."""
    path = _cache_path(ip)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state))
    _LOGGER.debug("Wrote cache for %s: %s", ip, state)
