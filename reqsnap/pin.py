"""Pin/unpin snapshots to mark them as reference baselines."""

from __future__ import annotations

from typing import Any, Dict, List

PIN_KEY = "pinned"


def pin_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of snapshot with pinned=True."""
    updated = dict(snapshot)
    updated[PIN_KEY] = True
    return updated


def unpin_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of snapshot with pinned removed (or False)."""
    updated = dict(snapshot)
    updated.pop(PIN_KEY, None)
    return updated


def is_pinned(snapshot: Dict[str, Any]) -> bool:
    """Return True if the snapshot is pinned."""
    return bool(snapshot.get(PIN_KEY, False))


def filter_pinned(snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return only pinned snapshots from the list."""
    return [s for s in snapshots if is_pinned(s)]


def filter_unpinned(snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return only unpinned snapshots from the list."""
    return [s for s in snapshots if not is_pinned(s)]


def list_pinned_ids(snapshots: List[Dict[str, Any]]) -> List[str]:
    """Return snapshot IDs (or URLs) for all pinned snapshots."""
    result: List[str] = []
    for snap in snapshots:
        if is_pinned(snap):
            identifier = snap.get("id") or snap.get("url", "unknown")
            result.append(str(identifier))
    return result
