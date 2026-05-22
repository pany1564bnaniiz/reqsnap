"""Filter and search utilities for request snapshots."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


def _matches_status(snapshot: Dict[str, Any], status: Optional[int]) -> bool:
    """Return True if snapshot status code matches the given status."""
    if status is None:
        return True
    return snapshot.get("status_code") == status


def _matches_environment(snapshot: Dict[str, Any], environment: Optional[str]) -> bool:
    """Return True if snapshot environment matches the given environment."""
    if environment is None:
        return True
    return snapshot.get("environment", "").lower() == environment.lower()


def _matches_url_pattern(snapshot: Dict[str, Any], pattern: Optional[str]) -> bool:
    """Return True if snapshot URL contains the given pattern substring."""
    if pattern is None:
        return True
    return pattern.lower() in snapshot.get("url", "").lower()


def _matches_method(snapshot: Dict[str, Any], method: Optional[str]) -> bool:
    """Return True if snapshot HTTP method matches."""
    if method is None:
        return True
    return snapshot.get("method", "").upper() == method.upper()


def filter_snapshots(
    snapshots: List[Dict[str, Any]],
    *,
    status: Optional[int] = None,
    environment: Optional[str] = None,
    url_pattern: Optional[str] = None,
    method: Optional[str] = None,
    custom: Optional[Callable[[Dict[str, Any]], bool]] = None,
) -> List[Dict[str, Any]]:
    """Filter a list of snapshot dicts by one or more criteria.

    Args:
        snapshots: List of snapshot dictionaries to filter.
        status: HTTP status code to match (e.g. 200, 404).
        environment: Environment label to match (case-insensitive).
        url_pattern: Substring to search for in the URL (case-insensitive).
        method: HTTP method to match (case-insensitive).
        custom: Optional callable that receives a snapshot dict and returns bool.

    Returns:
        Filtered list of snapshot dicts.
    """
    result = []
    for snap in snapshots:
        if not _matches_status(snap, status):
            continue
        if not _matches_environment(snap, environment):
            continue
        if not _matches_url_pattern(snap, url_pattern):
            continue
        if not _matches_method(snap, method):
            continue
        if custom is not None and not custom(snap):
            continue
        result.append(snap)
    return result
