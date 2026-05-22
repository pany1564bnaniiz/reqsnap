"""Tests for reqsnap.storage module."""

import json
import pytest
from pathlib import Path

from reqsnap.storage import (
    save_snapshot,
    load_snapshot,
    list_snapshots,
    delete_snapshot,
)


SAMPLE_SNAPSHOT = {
    "url": "https://api.example.com/users",
    "method": "GET",
    "status_code": 200,
    "headers": {"Content-Type": "application/json"},
    "body": '{"id": 1}',
    "environment": "production",
    "timestamp": "2024-01-01T00:00:00",
}


@pytest.fixture()
def tmp_store(tmp_path):
    """Return a temporary directory string for storage tests."""
    return str(tmp_path / "snaps")


class TestSaveSnapshot:
    def test_creates_file(self, tmp_store):
        path = save_snapshot(SAMPLE_SNAPSHOT, "snap1", base_dir=tmp_store)
        assert path.exists()

    def test_file_contains_valid_json(self, tmp_store):
        path = save_snapshot(SAMPLE_SNAPSHOT, "snap2", base_dir=tmp_store)
        data = json.loads(path.read_text())
        assert data["url"] == SAMPLE_SNAPSHOT["url"]

    def test_returns_path_object(self, tmp_store):
        path = save_snapshot(SAMPLE_SNAPSHOT, "snap3", base_dir=tmp_store)
        assert isinstance(path, Path)

    def test_creates_directory_if_missing(self, tmp_path):
        store = str(tmp_path / "new" / "nested" / "dir")
        path = save_snapshot(SAMPLE_SNAPSHOT, "snap4", base_dir=store)
        assert path.exists()


class TestLoadSnapshot:
    def test_loads_saved_snapshot(self, tmp_store):
        save_snapshot(SAMPLE_SNAPSHOT, "mysnap", base_dir=tmp_store)
        loaded = load_snapshot("mysnap", base_dir=tmp_store)
        assert loaded["status_code"] == 200

    def test_raises_file_not_found_for_missing(self, tmp_store):
        with pytest.raises(FileNotFoundError):
            load_snapshot("nonexistent", base_dir=tmp_store)

    def test_round_trip_preserves_all_fields(self, tmp_store):
        save_snapshot(SAMPLE_SNAPSHOT, "rt", base_dir=tmp_store)
        loaded = load_snapshot("rt", base_dir=tmp_store)
        assert loaded == SAMPLE_SNAPSHOT


class TestListSnapshots:
    def test_returns_empty_list_when_no_snapshots(self, tmp_store):
        assert list_snapshots(base_dir=tmp_store) == []

    def test_lists_saved_snapshots(self, tmp_store):
        save_snapshot(SAMPLE_SNAPSHOT, "alpha", base_dir=tmp_store)
        save_snapshot(SAMPLE_SNAPSHOT, "beta", base_dir=tmp_store)
        names = list_snapshots(base_dir=tmp_store)
        assert names == ["alpha", "beta"]

    def test_results_are_sorted(self, tmp_store):
        for name in ["zebra", "apple", "mango"]:
            save_snapshot(SAMPLE_SNAPSHOT, name, base_dir=tmp_store)
        assert list_snapshots(base_dir=tmp_store) == ["apple", "mango", "zebra"]


class TestDeleteSnapshot:
    def test_deletes_existing_snapshot(self, tmp_store):
        save_snapshot(SAMPLE_SNAPSHOT, "todel", base_dir=tmp_store)
        result = delete_snapshot("todel", base_dir=tmp_store)
        assert result is True
        assert list_snapshots(base_dir=tmp_store) == []

    def test_returns_false_for_missing_snapshot(self, tmp_store):
        result = delete_snapshot("ghost", base_dir=tmp_store)
        assert result is False
