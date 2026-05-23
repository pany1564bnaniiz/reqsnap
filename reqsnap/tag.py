"""Tagging support for snapshots — attach, remove, and filter by tags."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional


def add_tag(snapshot: dict, tag: str) -> dict:
    """Return a copy of the snapshot with the given tag added."""
    tags: List[str] = list(snapshot.get("tags", []))
    if tag not in tags:
        tags.append(tag)
    return {**snapshot, "tags": tags}


def remove_tag(snapshot: dict, tag: str) -> dict:
    """Return a copy of the snapshot with the given tag removed."""
    tags: List[str] = [t for t in snapshot.get("tags", []) if t != tag]
    return {**snapshot, "tags": tags}


def has_tag(snapshot: dict, tag: str) -> bool:
    """Return True if the snapshot contains the given tag."""
    return tag in snapshot.get("tags", [])


def filter_by_tags(
    snapshots: List[dict],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> List[dict]:
    """Filter snapshots by required and excluded tags.

    Args:
        snapshots: List of snapshot dicts.
        include: Only keep snapshots that have ALL of these tags.
        exclude: Drop snapshots that have ANY of these tags.

    Returns:
        Filtered list of snapshot dicts.
    """
    result = snapshots
    if include:
        result = [s for s in result if all(has_tag(s, t) for t in include)]
    if exclude:
        result = [s for s in result if not any(has_tag(s, t) for t in exclude)]
    return result


def list_tags(snapshots: List[dict]) -> List[str]:
    """Return a sorted, deduplicated list of all tags across snapshots."""
    seen: set = set()
    for s in snapshots:
        seen.update(s.get("tags", []))
    return sorted(seen)
