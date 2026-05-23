"""Utilities for renaming (aliasing) saved snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


def _load(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def set_alias(snapshot: Dict[str, Any], alias: str) -> Dict[str, Any]:
    """Return a copy of *snapshot* with the given *alias* set."""
    if not alias or not alias.strip():
        raise ValueError("alias must be a non-empty string")
    updated = dict(snapshot)
    updated["alias"] = alias.strip()
    return updated


def clear_alias(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of *snapshot* with the alias removed (if present)."""
    updated = dict(snapshot)
    updated.pop("alias", None)
    return updated


def get_alias(snapshot: Dict[str, Any]) -> str | None:
    """Return the alias stored in *snapshot*, or ``None`` if absent."""
    return snapshot.get("alias")


def rename_snapshot_file(path: Path, alias: str) -> Dict[str, Any]:
    """Load the snapshot at *path*, set *alias*, persist it, and return the updated dict."""
    data = _load(path)
    updated = set_alias(data, alias)
    _save(path, updated)
    return updated


def find_by_alias(snapshots: list[Dict[str, Any]], alias: str) -> list[Dict[str, Any]]:
    """Return all snapshots whose alias matches *alias* (case-insensitive)."""
    needle = alias.strip().lower()
    return [s for s in snapshots if (s.get("alias") or "").lower() == needle]
