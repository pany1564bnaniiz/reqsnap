"""Snapshot scoring — assign a numeric quality/relevance score to a snapshot."""

from __future__ import annotations

from typing import Any, Dict, List

# Weights used when computing the composite score (all positive, sum to 1.0)
_WEIGHTS: Dict[str, float] = {
    "has_body": 0.25,
    "has_headers": 0.15,
    "status_ok": 0.20,
    "is_pinned": 0.15,
    "has_tags": 0.10,
    "has_annotation": 0.10,
    "has_alias": 0.05,
}


def _score_components(snapshot: Dict[str, Any]) -> Dict[str, float]:
    """Return a dict mapping each scoring criterion to 0.0 or its weight."""
    body = snapshot.get("body") or snapshot.get("response_body", "")
    headers = snapshot.get("headers") or snapshot.get("response_headers", {})
    status = snapshot.get("status_code", 0)

    return {
        "has_body": _WEIGHTS["has_body"] if bool(body) else 0.0,
        "has_headers": _WEIGHTS["has_headers"] if bool(headers) else 0.0,
        "status_ok": _WEIGHTS["status_ok"] if 200 <= int(status) < 300 else 0.0,
        "is_pinned": _WEIGHTS["is_pinned"] if snapshot.get("pinned") is True else 0.0,
        "has_tags": _WEIGHTS["has_tags"] if bool(snapshot.get("tags")) else 0.0,
        "has_annotation": (
            _WEIGHTS["has_annotation"] if bool(snapshot.get("annotations")) else 0.0
        ),
        "has_alias": _WEIGHTS["has_alias"] if bool(snapshot.get("alias")) else 0.0,
    }


def score_snapshot(snapshot: Dict[str, Any]) -> float:
    """Return a composite quality score in [0.0, 1.0] for *snapshot*."""
    components = _score_components(snapshot)
    return round(sum(components.values()), 4)


def score_details(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Return a dict with the total score and a per-criterion breakdown."""
    components = _score_components(snapshot)
    return {
        "score": round(sum(components.values()), 4),
        "breakdown": {k: round(v, 4) for k, v in components.items()},
    }


def rank_snapshots(
    snapshots: List[Dict[str, Any]], descending: bool = True
) -> List[Dict[str, Any]]:
    """Return *snapshots* sorted by score.

    Each item in the returned list is the original snapshot dict augmented with
    a ``"_score"`` key so callers can inspect the value without re-computing.
    """
    scored = [{**snap, "_score": score_snapshot(snap)} for snap in snapshots]
    return sorted(scored, key=lambda s: s["_score"], reverse=descending)
