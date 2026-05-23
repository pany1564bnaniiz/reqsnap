"""Group snapshots by a given field for batch analysis."""

from typing import Any, Dict, List


SUPPORTED_FIELDS = ("url", "method", "status_code", "environment")


def group_by(snapshots: List[Dict], field: str) -> Dict[str, List[Dict]]:
    """Group a list of snapshots by the value of *field*.

    Args:
        snapshots: List of snapshot dicts as produced by ``to_dict``.
        field: Top-level key to group on.  Must be one of
               ``SUPPORTED_FIELDS``.

    Returns:
        Ordered dict mapping each distinct field value (as a string) to the
        list of snapshots that share that value.

    Raises:
        ValueError: If *field* is not in ``SUPPORTED_FIELDS``.
    """
    if field not in SUPPORTED_FIELDS:
        raise ValueError(
            f"Unsupported group field '{field}'. "
            f"Choose one of: {', '.join(SUPPORTED_FIELDS)}"
        )

    groups: Dict[str, List[Dict]] = {}
    for snap in snapshots:
        key = str(snap.get(field, ""))
        groups.setdefault(key, []).append(snap)
    return groups


def group_summary(groups: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
    """Return a lightweight summary list for *groups*.

    Each entry contains:
    - ``key``   – the group value
    - ``count`` – number of snapshots in the group
    - ``urls``  – deduplicated list of URLs present in the group
    """
    summary = []
    for key, snaps in groups.items():
        urls = list({s.get("url", "") for s in snaps})
        summary.append({"key": key, "count": len(snaps), "urls": sorted(urls)})
    return sorted(summary, key=lambda e: e["key"])


def largest_group(groups: Dict[str, List[Dict]]) -> str:
    """Return the key of the group with the most snapshots.

    Returns an empty string when *groups* is empty.
    """
    if not groups:
        return ""
    return max(groups, key=lambda k: len(groups[k]))
