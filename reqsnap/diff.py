"""Diff module for comparing API response snapshots across environments."""

import json
from typing import Any, Dict, List, Optional


DIFF_ADDED = "added"
DIFF_REMOVED = "removed"
DIFF_CHANGED = "changed"
DIFF_UNCHANGED = "unchanged"


def _compare_values(key: str, val_a: Any, val_b: Any) -> Dict:
    """Compare two values and return a diff entry."""
    if val_a == val_b:
        return {"key": key, "status": DIFF_UNCHANGED, "left": val_a, "right": val_b}
    return {"key": key, "status": DIFF_CHANGED, "left": val_a, "right": val_b}


def diff_snapshots(snapshot_a: Dict, snapshot_b: Dict) -> Dict:
    """Compare two snapshot dicts and return a structured diff report.

    Args:
        snapshot_a: First snapshot dict (e.g., from environment A).
        snapshot_b: Second snapshot dict (e.g., from environment B).

    Returns:
        A dict containing metadata and a list of field-level diff entries.
    """
    fields_to_compare = ["status_code", "url", "method", "environment"]
    diffs: List[Dict] = []

    for field in fields_to_compare:
        val_a = snapshot_a.get(field)
        val_b = snapshot_b.get(field)
        if val_a is None and val_b is None:
            continue
        elif val_a is None:
            diffs.append({"key": field, "status": DIFF_ADDED, "left": None, "right": val_b})
        elif val_b is None:
            diffs.append({"key": field, "status": DIFF_REMOVED, "left": val_a, "right": None})
        else:
            diffs.append(_compare_values(field, val_a, val_b))

    # Compare response body keys if both are dicts
    body_a = snapshot_a.get("body")
    body_b = snapshot_b.get("body")
    body_diffs = diff_bodies(body_a, body_b)
    diffs.extend(body_diffs)

    changed = any(d["status"] != DIFF_UNCHANGED for d in diffs)

    return {
        "environment_a": snapshot_a.get("environment", "unknown"),
        "environment_b": snapshot_b.get("environment", "unknown"),
        "has_diff": changed,
        "diffs": diffs,
    }


def diff_bodies(body_a: Optional[Any], body_b: Optional[Any]) -> List[Dict]:
    """Compare two response bodies and return field-level diffs."""
    results: List[Dict] = []

    if not isinstance(body_a, dict) or not isinstance(body_b, dict):
        if body_a != body_b:
            results.append({"key": "body", "status": DIFF_CHANGED, "left": body_a, "right": body_b})
        return results

    all_keys = set(body_a.keys()) | set(body_b.keys())
    for key in sorted(all_keys):
        prefixed = f"body.{key}"
        if key not in body_a:
            results.append({"key": prefixed, "status": DIFF_ADDED, "left": None, "right": body_b[key]})
        elif key not in body_b:
            results.append({"key": prefixed, "status": DIFF_REMOVED, "left": body_a[key], "right": None})
        else:
            results.append(_compare_values(prefixed, body_a[key], body_b[key]))

    return results


def filter_diffs(diff_report: Dict, statuses: Optional[List[str]] = None) -> Dict:
    """Return a copy of the diff report containing only entries matching the given statuses.

    Args:
        diff_report: A diff report as returned by ``diff_snapshots``.
        statuses: A list of status strings to keep (e.g., ``[DIFF_CHANGED, DIFF_ADDED]``).
                  If ``None`` or empty, all entries are returned unchanged.

    Returns:
        A new diff report dict with the ``diffs`` list filtered to matching statuses
        and ``has_diff`` recalculated accordingly.
    """
    if not statuses:
        return diff_report

    filtered = [d for d in diff_report.get("diffs", []) if d["status"] in statuses]
    return {
        **diff_report,
        "diffs": filtered,
        "has_diff": any(d["status"] != DIFF_UNCHANGED for d in filtered),
    }


def diff_to_json(diff_report: Dict, indent: int = 2) -> str:
    """Serialize a diff report to a JS
