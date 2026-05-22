"""Snapshot storage: save and load snapshots from disk."""

import json
import os
from pathlib import Path
from typing import List, Optional

DEFAULT_SNAPSHOT_DIR = ".reqsnap"


def _snapshot_dir(base_dir: Optional[str] = None) -> Path:
    """Return the snapshot directory, creating it if needed."""
    directory = Path(base_dir or DEFAULT_SNAPSHOT_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_snapshot(snapshot_dict: dict, name: str, base_dir: Optional[str] = None) -> Path:
    """Persist a snapshot dict to a JSON file.

    Args:
        snapshot_dict: Serialisable snapshot (output of ``to_dict``).
        name: Logical name used as the filename stem.
        base_dir: Override the default storage directory.

    Returns:
        Path to the written file.
    """
    directory = _snapshot_dir(base_dir)
    file_path = directory / f"{name}.json"
    with file_path.open("w", encoding="utf-8") as fh:
        json.dump(snapshot_dict, fh, indent=2)
    return file_path


def load_snapshot(name: str, base_dir: Optional[str] = None) -> dict:
    """Load a snapshot from disk by name.

    Args:
        name: Logical name (filename stem) of the snapshot.
        base_dir: Override the default storage directory.

    Returns:
        The snapshot as a dict.

    Raises:
        FileNotFoundError: If the snapshot file does not exist.
    """
    directory = _snapshot_dir(base_dir)
    file_path = directory / f"{name}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found at {file_path}")
    with file_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def list_snapshots(base_dir: Optional[str] = None) -> List[str]:
    """Return the names of all stored snapshots.

    Args:
        base_dir: Override the default storage directory.

    Returns:
        Sorted list of snapshot name strings.
    """
    directory = _snapshot_dir(base_dir)
    return sorted(p.stem for p in directory.glob("*.json"))


def delete_snapshot(name: str, base_dir: Optional[str] = None) -> bool:
    """Delete a snapshot file by name.

    Returns:
        True if deleted, False if it did not exist.
    """
    directory = _snapshot_dir(base_dir)
    file_path = directory / f"{name}.json"
    if file_path.exists():
        file_path.unlink()
        return True
    return False
