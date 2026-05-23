"""Tests for reqsnap/archive.py"""

import json
import zipfile
from pathlib import Path

import pytest

from reqsnap.archive import (
    archive_snapshots,
    list_archive_contents,
    restore_snapshots,
)


@pytest.fixture()
def snap_dir(tmp_path):
    return tmp_path


def _write_snap(directory: Path, name: str, data: dict) -> Path:
    p = directory / name
    p.write_text(json.dumps(data))
    return p


@pytest.fixture()
def two_snaps(snap_dir):
    a = _write_snap(snap_dir, "snap_a.json", {"url": "https://a.example.com", "status_code": 200})
    b = _write_snap(snap_dir, "snap_b.json", {"url": "https://b.example.com", "status_code": 404})
    return [a, b]


class TestArchiveSnapshots:
    def test_creates_zip_file(self, two_snaps, tmp_path):
        out = tmp_path / "out.zip"
        result = archive_snapshots(two_snaps, output_path=out)
        assert result.exists()
        assert result.suffix == ".zip"

    def test_returns_path_to_archive(self, two_snaps, tmp_path):
        out = tmp_path / "result.zip"
        result = archive_snapshots(two_snaps, output_path=out)
        assert isinstance(result, Path)
        assert result == out

    def test_archive_contains_both_files(self, two_snaps, tmp_path):
        out = tmp_path / "both.zip"
        archive_snapshots(two_snaps, output_path=out)
        with zipfile.ZipFile(out, "r") as zf:
            names = zf.namelist()
        assert "snap_a.json" in names
        assert "snap_b.json" in names

    def test_delete_originals_removes_files(self, two_snaps, tmp_path):
        out = tmp_path / "del.zip"
        archive_snapshots(two_snaps, output_path=out, delete_originals=True)
        for p in two_snaps:
            assert not p.exists()

    def test_delete_false_keeps_originals(self, two_snaps, tmp_path):
        out = tmp_path / "keep.zip"
        archive_snapshots(two_snaps, output_path=out, delete_originals=False)
        for p in two_snaps:
            assert p.exists()

    def test_raises_on_empty_list(self, tmp_path):
        with pytest.raises(ValueError, match="No snapshot paths"):
            archive_snapshots([], output_path=tmp_path / "empty.zip")

    def test_raises_on_missing_file(self, tmp_path):
        missing = tmp_path / "ghost.json"
        with pytest.raises(FileNotFoundError):
            archive_snapshots([missing], output_path=tmp_path / "x.zip")

    def test_default_output_name_contains_timestamp(self, two_snaps, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = archive_snapshots(two_snaps)
        assert result.name.startswith("reqsnap_archive_")
        assert result.suffix == ".zip"


class TestRestoreSnapshots:
    def test_restores_files_to_output_dir(self, two_snaps, tmp_path):
        archive = tmp_path / "arc.zip"
        restore_dir = tmp_path / "restored"
        archive_snapshots(two_snaps, output_path=archive)
        restored = restore_snapshots(archive, restore_dir)
        assert len(restored) == 2
        assert all(p.exists() for p in restored)

    def test_restored_content_matches_original(self, snap_dir, tmp_path):
        data = {"url": "https://example.com", "status_code": 200}
        snap = _write_snap(snap_dir, "snap_x.json", data)
        archive = tmp_path / "single.zip"
        archive_snapshots([snap], output_path=archive)
        restore_dir = tmp_path / "out"
        restored = restore_snapshots(archive, restore_dir)
        assert json.loads(restored[0].read_text()) == data

    def test_raises_on_missing_archive(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            restore_snapshots(tmp_path / "nope.zip", tmp_path / "out")

    def test_creates_output_dir_if_missing(self, two_snaps, tmp_path):
        archive = tmp_path / "arc2.zip"
        restore_dir = tmp_path / "new" / "nested"
        archive_snapshots(two_snaps, output_path=archive)
        restore_snapshots(archive, restore_dir)
        assert restore_dir.exists()


class TestListArchiveContents:
    def test_returns_list_of_names(self, two_snaps, tmp_path):
        out = tmp_path / "list.zip"
        archive_snapshots(two_snaps, output_path=out)
        names = list_archive_contents(out)
        assert set(names) == {"snap_a.json", "snap_b.json"}

    def test_raises_on_missing_archive(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            list_archive_contents(tmp_path / "missing.zip")
