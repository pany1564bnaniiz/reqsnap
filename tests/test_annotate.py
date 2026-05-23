"""Tests for reqsnap.annotate."""

import json
import pytest

from reqsnap.annotate import (
    add_annotation,
    annotations_to_json,
    list_annotations,
    remove_annotation,
)


def _make_snap(**kwargs):
    base = {"url": "https://example.com", "method": "GET", "status_code": 200}
    base.update(kwargs)
    return base


class TestAddAnnotation:
    def test_adds_annotation_to_empty(self):
        snap = _make_snap()
        result = add_annotation(snap, "first note")
        assert len(result["annotations"]) == 1

    def test_annotation_contains_note(self):
        snap = _make_snap()
        result = add_annotation(snap, "hello world")
        assert result["annotations"][0]["note"] == "hello world"

    def test_default_author_is_reqsnap(self):
        snap = _make_snap()
        result = add_annotation(snap, "note")
        assert result["annotations"][0]["author"] == "reqsnap"

    def test_custom_author_is_preserved(self):
        snap = _make_snap()
        result = add_annotation(snap, "note", author="alice")
        assert result["annotations"][0]["author"] == "alice"

    def test_timestamp_is_present(self):
        snap = _make_snap()
        result = add_annotation(snap, "note")
        assert "timestamp" in result["annotations"][0]

    def test_does_not_mutate_original(self):
        snap = _make_snap()
        add_annotation(snap, "note")
        assert "annotations" not in snap

    def test_accumulates_multiple_annotations(self):
        snap = _make_snap()
        snap = add_annotation(snap, "first")
        snap = add_annotation(snap, "second")
        assert len(snap["annotations"]) == 2


class TestRemoveAnnotation:
    def test_removes_correct_index(self):
        snap = _make_snap()
        snap = add_annotation(snap, "keep")
        snap = add_annotation(snap, "remove me")
        result = remove_annotation(snap, 1)
        assert len(result["annotations"]) == 1
        assert result["annotations"][0]["note"] == "keep"

    def test_raises_on_invalid_index(self):
        snap = add_annotation(_make_snap(), "only")
        with pytest.raises(IndexError):
            remove_annotation(snap, 5)

    def test_does_not_mutate_original(self):
        snap = add_annotation(_make_snap(), "note")
        remove_annotation(snap, 0)
        assert len(snap["annotations"]) == 1


class TestListAnnotations:
    def test_returns_empty_list_when_none(self):
        snap = _make_snap()
        assert list_annotations(snap) == []

    def test_returns_all_annotations(self):
        snap = add_annotation(add_annotation(_make_snap(), "a"), "b")
        assert len(list_annotations(snap)) == 2


class TestAnnotationsToJson:
    def test_returns_valid_json(self):
        snap = add_annotation(_make_snap(), "test note")
        raw = annotations_to_json(snap)
        parsed = json.loads(raw)
        assert isinstance(parsed, list)

    def test_empty_when_no_annotations(self):
        snap = _make_snap()
        raw = annotations_to_json(snap)
        assert json.loads(raw) == []
