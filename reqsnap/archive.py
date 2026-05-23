"""Archive and restore snapshots — compress old snapshots into a zip archive."""

import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def _default_archive_name() -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"reqsnap_archive_{timestamp}.zip"


def archive_snapshots(
    snapshot_paths: List[Path],
    output_path: Optional[Path] = None,
    delete_originals: bool = False,
) -> Path:
    """Compress a list of snapshot files into a zip archive.

    Args:
        snapshot_paths: List of .json snapshot file paths to archive.
        output_path: Destination zip file path. Defaults to current directory.
        delete_originals: If True, remove original files after archiving.

    Returns:
        Path to the created archive file.
    """
    if not snapshot_paths:
        raise ValueError("No snapshot paths provided to archive.")

    if output_path is None:
        output_path = Path(".") / _default_archive_name()

    output_path = Path(output_path)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for snap_path in snapshot_paths:
            snap_path = Path(snap_path)
            if not snap_path.exists():
                raise FileNotFoundError(f"Snapshot file not found: {snap_path}")
            zf.write(snap_path, arcname=snap_path.name)

    if delete_originals:
        for snap_path in snapshot_paths:
            Path(snap_path).unlink(missing_ok=True)

    return output_path


def restore_snapshots(archive_path: Path, output_dir: Path) -> List[Path]:
    """Extract snapshots from a zip archive into output_dir.

    Args:
        archive_path: Path to the zip archive.
        output_dir: Directory where snapshots will be restored.

    Returns:
        List of restored snapshot file paths.
    """
    archive_path = Path(archive_path)
    output_dir = Path(output_dir)

    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    restored: List[Path] = []

    with zipfile.ZipFile(archive_path, "r") as zf:
        for member in zf.namelist():
            zf.extract(member, path=output_dir)
            restored.append(output_dir / member)

    return restored


def list_archive_contents(archive_path: Path) -> List[str]:
    """Return a list of filenames stored inside the archive."""
    archive_path = Path(archive_path)
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    with zipfile.ZipFile(archive_path, "r") as zf:
        return zf.namelist()
