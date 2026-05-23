"""Tests for reqsnap.commands.tag_cmd."""

import json
import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from reqsnap.commands.tag_cmd import handle_tag


def _make_args(tag_action, snapshot_id=None, tag_name=None, directory=None):
    args = argparse.Namespace(
        tag_action=tag_action,
        snapshot_id=snapshot_id,
        tag_name=tag_name,
        directory=directory,
    )
    return args


@pytest.fixture()
def snap_dir(tmp_path):
    return tmp_path


@pytest.fixture()
def snap_file(snap_dir):
    data = {"url": "https://example.com", "method": "GET", "status_code": 200, "tags": ["regression"]}
    p = snap_dir / "snap1.json"
    p.write_text(json.dumps(data))
    return p


class TestHandleTagList:
    def test_prints_tags(self, snap_dir, snap_file, capsys):
        args = _make_args("list", directory=str(snap_dir))
        handle_tag(args)
        captured = capsys.readouterr()
        assert "regression" in captured.out

    def test_no_tags_message(self, snap_dir, capsys):
        empty = snap_dir / "empty.json"
        empty.write_text(json.dumps({"url": "x", "tags": []}))
        args = _make_args("list", directory=str(snap_dir))
        handle_tag(args)
        captured = capsys.readouterr()
        assert "No tags found" in captured.out


class TestHandleTagAdd:
    def test_adds_tag_to_snapshot(self, snap_dir, snap_file):
        args = _make_args("add", snapshot_id="snap1", tag_name="smoke", directory=str(snap_dir))
        handle_tag(args)
        data = json.loads(snap_file.read_text())
        assert "smoke" in data["tags"]

    def test_prints_confirmation(self, snap_dir, snap_file, capsys):
        args = _make_args("add", snapshot_id="snap1", tag_name="smoke", directory=str(snap_dir))
        handle_tag(args)
        captured = capsys.readouterr()
        assert "smoke" in captured.out

    def test_exits_when_snapshot_not_found(self, snap_dir):
        args = _make_args("add", snapshot_id="missing", tag_name="smoke", directory=str(snap_dir))
        with pytest.raises(SystemExit):
            handle_tag(args)


class TestHandleTagRemove:
    def test_removes_tag_from_snapshot(self, snap_dir, snap_file):
        args = _make_args("remove", snapshot_id="snap1", tag_name="regression", directory=str(snap_dir))
        handle_tag(args)
        data = json.loads(snap_file.read_text())
        assert "regression" not in data["tags"]

    def test_noop_when_tag_absent(self, snap_dir, snap_file):
        args = _make_args("remove", snapshot_id="snap1", tag_name="nonexistent", directory=str(snap_dir))
        handle_tag(args)  # should not raise
        data = json.loads(snap_file.read_text())
        assert "regression" in data["tags"]

    def test_persists_changes_to_file(self, snap_dir, snap_file):
        args = _make_args("remove", snapshot_id="snap1", tag_name="regression", directory=str(snap_dir))
        handle_tag(args)
        data = json.loads(snap_file.read_text())
        assert isinstance(data["tags"], list)
