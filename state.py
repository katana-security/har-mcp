"""HAR state -- in-memory storage for the loaded HAR file."""

from typing import Any

_har_data: dict[str, Any] | None = None
_har_source: str | None = None


def get_har_data() -> dict[str, Any]:
    """Return the loaded HAR data, or raise if nothing is loaded."""
    if _har_data is None:
        raise ValueError("No HAR file loaded. Please load a HAR file first using load_har.")
    return _har_data


def set_har_data(data: dict[str, Any], source: str) -> None:
    """Store parsed HAR data and its source path/URL."""
    global _har_data, _har_source
    _har_data = data
    _har_source = source


def get_har_source() -> str | None:
    """Return the path or URL of the loaded HAR file."""
    return _har_source


def is_loaded() -> bool:
    """Return True if a HAR file is currently loaded."""
    return _har_data is not None


def get_entries() -> list[dict[str, Any]]:
    """Return the list of HAR entries, or an empty list if nothing is loaded."""
    if _har_data is None:
        return []
    return _har_data.get("log", {}).get("entries", [])


def get_entry_count() -> int:
    """Return the number of entries in the loaded HAR file."""
    return len(get_entries())
