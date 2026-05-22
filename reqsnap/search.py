"""High-level search interface combining storage and filter for snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from reqsnap.filter import filter_snapshots
from reqsnap.storage import list_snapshots, _snapshot_dir


def _load_snapshot_file(path: Path) -> Optional[Dict[str, Any]]:
    """Load a single snapshot JSON file; return None on error."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def search_snapshots(
    *,
    base_dir: Optional[Path] = None,
    status: Optional[int] = None,
    environment: Optional[str] = None,
    url_pattern: Optional[str] = None,
    method: Optional[str] = None,
    custom: Optional[Callable[[Dict[str, Any]], bool]] = None,
) -> List[Dict[str, Any]]:
    """Search persisted snapshots using filter criteria.

    Loads all snapshots from the storage directory, applies the requested
    filters, and returns matching snapshot dicts.

    Args:
        base_dir: Override the default snapshot storage directory.
        status: HTTP status code to match.
        environment: Environment label to match (case-insensitive).
        url_pattern: Substring to search in URL (case-insensitive).
        method: HTTP method to match (case-insensitive).
        custom: Optional callable for additional filtering logic.

    Returns:
        List of matching snapshot dicts, each including a ``_path`` key
        with the source file path as a string.
    """
    directory = base_dir if base_dir is not None else _snapshot_dir()
    paths = list_snapshots(base_dir=directory) if base_dir else list_snapshots()

    snapshots: List[Dict[str, Any]] = []
    for path in paths:
        data = _load_snapshot_file(path)
        if data is not None:
            data["_path"] = str(path)
            snapshots.append(data)

    return filter_snapshots(
        snapshots,
        status=status,
        environment=environment,
        url_pattern=url_pattern,
        method=method,
        custom=custom,
    )
