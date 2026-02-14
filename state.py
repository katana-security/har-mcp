"""HAR state -- registry for multiple loaded HAR files, keyed by label."""

from __future__ import annotations

import os
from typing import Any

_registry: dict[str, dict[str, Any]] = {}


def _derive_label(source: str) -> str:
    """Derive a short label from a file path or URL."""
    basename = os.path.basename(source)
    name, _ = os.path.splitext(basename)
    # Deduplicate: if label already exists, append a counter
    label = name
    counter = 2
    while label in _registry:
        label = f"{name}_{counter}"
        counter += 1
    return label


def set_har(label: str | None, data: dict[str, Any], source: str) -> str:
    """Store parsed HAR data under the given label. Returns the actual label used."""
    if not label:
        label = _derive_label(source)
    _registry[label] = {"data": data, "source": source}
    return label


def get_har(label: str) -> dict[str, Any]:
    """Return the HAR data dict for a label, or raise if not found."""
    if label not in _registry:
        loaded = ", ".join(_registry.keys()) if _registry else "none"
        raise ValueError(
            f"No HAR loaded with label '{label}'. Currently loaded: {loaded}"
        )
    return _registry[label]["data"]


def get_source(label: str) -> str:
    """Return the source path/URL for a loaded HAR."""
    if label not in _registry:
        raise ValueError(f"No HAR loaded with label '{label}'.")
    return _registry[label]["source"]


def remove_har(label: str) -> None:
    """Remove a loaded HAR from the registry."""
    _registry.pop(label, None)


def list_hars() -> list[dict[str, Any]]:
    """Return metadata for all loaded HARs."""
    result = []
    for label, entry in _registry.items():
        data = entry["data"]
        entries = data.get("log", {}).get("entries", [])
        result.append({
            "label": label,
            "source": entry["source"],
            "entry_count": len(entries),
        })
    return result


def get_entries(label: str) -> list[dict[str, Any]]:
    """Return the list of HAR entries for a label."""
    data = get_har(label)
    return data.get("log", {}).get("entries", [])


def get_entry_count(label: str) -> int:
    """Return the number of entries for a label."""
    return len(get_entries(label))


def is_loaded(label: str) -> bool:
    """Return True if a HAR with this label is loaded."""
    return label in _registry


def has_any() -> bool:
    """Return True if any HAR files are loaded."""
    return len(_registry) > 0
