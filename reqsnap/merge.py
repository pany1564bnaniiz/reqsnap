"""Merge multiple snapshots into a single aggregated snapshot."""

from typing import List, Dict, Any, Optional
from collections import Counter


def _most_common_value(values: list) -> Any:
    """Return the most frequently occurring value in a list."""
    if not values:
        return None
    counter = Counter(str(v) for v in values)
    most_common_str = counter.most_common(1)[0][0]
    # Return the original typed value
    for v in values:
        if str(v) == most_common_str:
            return v
    return values[0]


def merge_snapshots(snapshots: List[Dict[str, Any]], strategy: str = "latest") -> Dict[str, Any]:
    """Merge a list of snapshots into one.

    Args:
        snapshots: List of snapshot dicts to merge.
        strategy: One of 'latest', 'first', or 'majority'.
            - 'latest': use the last snapshot as the base.
            - 'first': use the first snapshot as the base.
            - 'majority': pick the most common value per field.

    Returns:
        A merged snapshot dict.

    Raises:
        ValueError: If snapshots is empty or strategy is unsupported.
    """
    if not snapshots:
        raise ValueError("Cannot merge an empty list of snapshots.")

    supported = {"latest", "first", "majority"}
    if strategy not in supported:
        raise ValueError(f"Unsupported strategy '{strategy}'. Choose from {supported}.")

    if strategy == "latest":
        base = dict(snapshots[-1])
    elif strategy == "first":
        base = dict(snapshots[0])
    else:  # majority
        fields = ["url", "method", "status_code", "body", "environment"]
        base = {}
        for field in fields:
            values = [s[field] for s in snapshots if field in s]
            base[field] = _most_common_value(values) if values else None
        # Carry over remaining keys from last snapshot
        for key in snapshots[-1]:
            if key not in base:
                base[key] = snapshots[-1][key]

    base["merged"] = True
    base["merged_count"] = len(snapshots)
    base["merge_strategy"] = strategy
    return base


def merge_summary(merged: Dict[str, Any]) -> str:
    """Return a human-readable summary of a merged snapshot."""
    count = merged.get("merged_count", 1)
    strategy = merged.get("merge_strategy", "unknown")
    url = merged.get("url", "(unknown)")
    method = merged.get("method", "GET")
    status = merged.get("status_code", "?")
    return (
        f"Merged {count} snapshot(s) using '{strategy}' strategy\n"
        f"  {method} {url} -> HTTP {status}"
    )
