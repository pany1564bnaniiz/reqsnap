"""Tests for reqsnap.rename."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from reqsnap.rename import (
    set_alias,
    clear_alias,
    get_alias,
    rename_snapshot_file,
    find_by_alias,
)


def _make_snap(alias: str | None = None) -> dict:
    snap = {"url": "https://example.com", "method": "GET", "status_code": 200}
    if alias is not None:
        snap["alias"] = alias
    return snap


@pytest.fixture()
def snap_file(tmp_path: Path) -> Path:
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(_make_snap()), encoding="utf-8")
    return p


class TestSetAlias:
    def test_adds_alias_key(self):
        result = set_alias(_make_snap(), "my-alias")
        assert result["alias"] == "my-alias"

    def test_does_not_mutate_original(self):
        snap = _make_snap()
        set_alias(snap, "x")
        assert "alias" not in snap

    def test_strips_whitespace(self):
        result = set_alias(_make_snap(), "  trimmed  ")
        assert result["alias"] == "trimmed"

    def test_raises_on_empty_alias(self):
        with pytest.raises(ValueError):
            set_alias(_make_snap(), "")

    def test_raises_on_whitespace_only_alias(self):
        with pytest.raises(ValueError):
            set_alias(_make_snap(), "   ")


class TestClearAlias:
    def test_removes_existing_alias(self):
        snap = _make_snap(alias="old")
        result = clear_alias(snap)
        assert "alias" not in result

    def test_no_error_when_alias_absent(self):
        snap = _make_snap()
        result = clear_alias(snap)
        assert "alias" not in result

    def test_does_not_mutate_original(self):
        snap = _make_snap(alias="keep")
        clear_alias(snap)
        assert snap["alias"] == "keep"


class TestGetAlias:
    def test_returns_alias_when_present(self):
        snap = _make_snap(alias="prod-health")
        assert get_alias(snap) == "prod-health"

    def test_returns_none_when_absent(self):
        assert get_alias(_make_snap()) is None


class TestRenameSnapshotFile:
    def test_persists_alias_to_disk(self, snap_file: Path):
        rename_snapshot_file(snap_file, "saved-alias")
        data = json.loads(snap_file.read_text(encoding="utf-8"))
        assert data["alias"] == "saved-alias"

    def test_returns_updated_dict(self, snap_file: Path):
        result = rename_snapshot_file(snap_file, "returned")
        assert result["alias"] == "returned"


class TestFindByAlias:
    def test_finds_matching_snapshot(self):
        snaps = [_make_snap(alias="alpha"), _make_snap(alias="beta")]
        result = find_by_alias(snaps, "alpha")
        assert len(result) == 1 and result[0]["alias"] == "alpha"

    def test_case_insensitive_match(self):
        snaps = [_make_snap(alias="Alpha")]
        assert len(find_by_alias(snaps, "alpha")) == 1

    def test_returns_empty_when_no_match(self):
        snaps = [_make_snap(alias="other")]
        assert find_by_alias(snaps, "missing") == []

    def test_returns_multiple_matches(self):
        snaps = [_make_snap(alias="dup"), _make_snap(alias="dup"), _make_snap(alias="x")]
        assert len(find_by_alias(snaps, "dup")) == 2
