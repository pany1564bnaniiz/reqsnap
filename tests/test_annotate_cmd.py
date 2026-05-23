"""Tests for reqsnap.commands.annotate_cmd."""

import json
import sys
import pytest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from reqsnap.commands.annotate_cmd import handle_annotate


def _make_args(**kwargs):
    defaults = {"annotate_action": "list", "snapshot": "", "author": "reqsnap"}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


@pytest.fixture()
def snap_file(tmp_path):
    data = {"url": "https://example.com", "method": "GET", "status_code": 200}
    p = tmp_path / "snap.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


class TestHandleAnnotateList:
    def test_prints_no_annotations_message(self, snap_file, capsys):
        args = _make_args(annotate_action="list", snapshot=str(snap_file))
        handle_annotate(args)
        out = capsys.readouterr().out
        assert "no annotations" in out

    def test_lists_existing_annotation(self, snap_file, capsys):
        data = json.loads(snap_file.read_text())
        from reqsnap.annotate import add_annotation
        data = add_annotation(data, "hello")
        snap_file.write_text(json.dumps(data))
        args = _make_args(annotate_action="list", snapshot=str(snap_file))
        handle_annotate(args)
        out = capsys.readouterr().out
        assert "hello" in out


class TestHandleAnnotateAdd:
    def test_adds_annotation_to_file(self, snap_file):
        args = _make_args(annotate_action="add", snapshot=str(snap_file), note="my note")
        handle_annotate(args)
        data = json.loads(snap_file.read_text())
        assert data["annotations"][0]["note"] == "my note"

    def test_prints_confirmation(self, snap_file, capsys):
        args = _make_args(annotate_action="add", snapshot=str(snap_file), note="x")
        handle_annotate(args)
        out = capsys.readouterr().out
        assert "added" in out

    def test_custom_author_stored(self, snap_file):
        args = _make_args(annotate_action="add", snapshot=str(snap_file), note="n", author="bob")
        handle_annotate(args)
        data = json.loads(snap_file.read_text())
        assert data["annotations"][0]["author"] == "bob"


class TestHandleAnnotateRemove:
    def test_removes_annotation(self, snap_file):
        from reqsnap.annotate import add_annotation
        data = json.loads(snap_file.read_text())
        data = add_annotation(data, "to remove")
        snap_file.write_text(json.dumps(data))
        args = _make_args(annotate_action="remove", snapshot=str(snap_file), index=0)
        handle_annotate(args)
        result = json.loads(snap_file.read_text())
        assert result["annotations"] == []

    def test_exits_on_invalid_index(self, snap_file):
        args = _make_args(annotate_action="remove", snapshot=str(snap_file), index=99)
        with pytest.raises(SystemExit):
            handle_annotate(args)


class TestHandleAnnotateErrors:
    def test_exits_when_file_missing(self, tmp_path):
        args = _make_args(annotate_action="list", snapshot=str(tmp_path / "missing.json"))
        with pytest.raises(SystemExit):
            handle_annotate(args)

    def test_exits_on_invalid_json(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("not json")
        args = _make_args(annotate_action="list", snapshot=str(bad))
        with pytest.raises(SystemExit):
            handle_annotate(args)
