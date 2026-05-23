"""Compare multiple snapshots across environments and summarize results."""

from typing import List, Dict, Any, Optional
from reqsnap.diff import diff_snapshots, filter_diffs


def compare_snapshots(
    snapshots: List[Dict[str, Any]],
    ignore_keys: Optional[List[str]] = None,
    only_diffs: bool = False,
) -> Dict[str, Any]:
    """Compare a list of snapshots pairwise and return a summary report.

    Args:
        snapshots: List of snapshot dicts (from RequestSnapshot.to_dict).
        ignore_keys: Body keys to ignore during comparison.
        only_diffs: If True, only include pairs that have differences.

    Returns:
        A dict with 'total', 'differing', 'identical', and 'comparisons' keys.
    """
    if len(snapshots) < 2:
        raise ValueError("At least two snapshots are required for comparison.")

    comparisons = []
    for i in range(len(snapshots) - 1):
        snap_a = snapshots[i]
        snap_b = snapshots[i + 1]
        result = diff_snapshots(snap_a, snap_b)
        if ignore_keys:
            result["changes"] = filter_diffs(result.get("changes", []), ignore_keys)
            result["has_diff"] = bool(result["changes"])
        comparisons.append(result)

    if only_diffs:
        comparisons = [c for c in comparisons if c.get("has_diff")]

    differing = sum(1 for c in comparisons if c.get("has_diff"))
    identical = len(comparisons) - differing

    return {
        "total": len(comparisons),
        "differing": differing,
        "identical": identical,
        "comparisons": comparisons,
    }


def summarize_comparison(report: Dict[str, Any]) -> str:
    """Return a human-readable summary string for a comparison report."""
    lines = [
        f"Comparisons : {report['total']}",
        f"Identical   : {report['identical']}",
        f"Differing   : {report['differing']}",
    ]
    for idx, comp in enumerate(report["comparisons"], start=1):
        env_a = comp.get("environment_a", "?")
        env_b = comp.get("environment_b", "?")
        status = "DIFF" if comp.get("has_diff") else "SAME"
        lines.append(f"  [{idx}] {env_a} vs {env_b}: {status}")
    return "\n".join(lines)
