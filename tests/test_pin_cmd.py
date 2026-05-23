"""Tests for reqsnap.commands.pin_cmd."""

import json
import sys
from argparse import Namespace
from pathlib import Path

import pytest

from reqsnap.commands.pin_cmd import handle_pin


def _make_args(action, snapshot):
    return Namespace(action=action, snapshot=str(snapshot))


@pytest.fixture()
def snap_file(tmp_path):
    data = {"url": "https://api.example.com", "method": "GET", "status_code": 200}
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


@pytest.fixture()
def pinned_file(tmp_path):
    data = {"url": "https://api.example.com", "method": "GET", "status_code": 200, "pinned": True}
    p = tmp_path / "pinned.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


class TestHandlePin:
    def test_pin_sets_pinned_true(self, snap_file):
        handle_pin(_make_args("pin", snap_file))
        data = json.loads(snap_file.read_text())
        assert data["pinned"] is True

    def test_unpin_removes_pinned(self, pinned_file):
        handle_pin(_make_args("unpin", pinned_file))
        data = json.loads(pinned_file.read_text())
        assert "pinned" not in data

    def test_status_pinned_prints_pinned(self, pinned_file, capsys):
        handle_pin(_make_args("status", pinned_file))
        out = capsys.readouterr().out
        assert "pinned" in out

    def test_status_unpinned_prints_unpinned(self, snap_file, capsys):
        handle_pin(_make_args("status", snap_file))
        out = capsys.readouterr().out
        assert "unpinned" in out

    def test_missing_file_exits(self, tmp_path):
        args = _make_args("pin", tmp_path / "nonexistent.json")
        with pytest.raises(SystemExit):
            handle_pin(args)

    def test_pin_prints_confirmation(self, snap_file, capsys):
        handle_pin(_make_args("pin", snap_file))
        out = capsys.readouterr().out
        assert "Pinned" in out

    def test_unpin_prints_confirmation(self, pinned_file, capsys):
        handle_pin(_make_args("unpin", pinned_file))
        out = capsys.readouterr().out
        assert "Unpinned" in out


class TestHandlePinList:
    def test_list_shows_pinned_snapshots(self, tmp_path, capsys):
        for i, pinned in enumerate([True, False, True]):
            data = {"id": f"snap-{i}", "url": f"https://api.example.com/{i}", "pinned": pinned} if pinned else {"id": f"snap-{i}", "url": f"https://api.example.com/{i}"}
            (tmp_path / f"snap-{i}.json").write_text(json.dumps(data))
        handle_pin(_make_args("list", tmp_path))
        out = capsys.readouterr().out
        assert "snap-0" in out
        assert "snap-2" in out
        assert "snap-1" not in out

    def test_list_no_pinned_shows_message(self, tmp_path, capsys):
        data = {"url": "https://api.example.com", "method": "GET"}
        (tmp_path / "snap.json").write_text(json.dumps(data))
        handle_pin(_make_args("list", tmp_path))
        out = capsys.readouterr().out
        assert "No pinned" in out
