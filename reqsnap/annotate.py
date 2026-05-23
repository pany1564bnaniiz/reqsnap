"""Annotation support for request snapshots."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def add_annotation(snapshot: dict, note: str, author: str = "reqsnap") -> dict:
    """Return a new snapshot dict with an annotation appended."""
    snapshot = dict(snapshot)
    annotations = list(snapshot.get("annotations", []))
    annotations.append(
        {
            "note": note,
            "author": author,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    snapshot["annotations"] = annotations
    return snapshot


def remove_annotation(snapshot: dict, index: int) -> dict:
    """Return a new snapshot dict with the annotation at *index* removed."""
    snapshot = dict(snapshot)
    annotations = list(snapshot.get("annotations", []))
    if index < 0 or index >= len(annotations):
        raise IndexError(f"Annotation index {index} out of range (0-{len(annotations) - 1}).")
    annotations.pop(index)
    snapshot["annotations"] = annotations
    return snapshot


def list_annotations(snapshot: dict) -> list[dict]:
    """Return the list of annotations attached to *snapshot*."""
    return list(snapshot.get("annotations", []))


def annotations_to_json(snapshot: dict, indent: int = 2) -> str:
    """Serialise the annotations of *snapshot* to a JSON string."""
    return json.dumps(list_annotations(snapshot), indent=indent)
