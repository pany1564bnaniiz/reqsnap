"""Tests for reqsnap.tag module."""

import pytest
from reqsnap.tag import add_tag, remove_tag, has_tag, filter_by_tags, list_tags


def _make_snap(tags=None, **kwargs):
    base = {"url": "https://example.com", "method": "GET", "status_code": 200}
    if tags is not None:
        base["tags"] = tags
    base.update(kwargs)
    return base


class TestAddTag:
    def test_adds_tag_to_empty(self):
        snap = _make_snap()
        result = add_tag(snap, "smoke")
        assert "smoke" in result["tags"]

    def test_does_not_duplicate_tag(self):
        snap = _make_snap(tags=["smoke"])
        result = add_tag(snap, "smoke")
        assert result["tags"].count("smoke") == 1

    def test_does_not_mutate_original(self):
        snap = _make_snap(tags=["a"])
        add_tag(snap, "b")
        assert "b" not in snap.get("tags", [])

    def test_preserves_existing_tags(self):
        snap = _make_snap(tags=["regression"])
        result = add_tag(snap, "smoke")
        assert "regression" in result["tags"]
        assert "smoke" in result["tags"]


class TestRemoveTag:
    def test_removes_existing_tag(self):
        snap = _make_snap(tags=["smoke", "regression"])
        result = remove_tag(snap, "smoke")
        assert "smoke" not in result["tags"]

    def test_noop_when_tag_absent(self):
        snap = _make_snap(tags=["regression"])
        result = remove_tag(snap, "smoke")
        assert result["tags"] == ["regression"]

    def test_does_not_mutate_original(self):
        snap = _make_snap(tags=["smoke"])
        remove_tag(snap, "smoke")
        assert "smoke" in snap["tags"]


class TestHasTag:
    def test_true_when_present(self):
        snap = _make_snap(tags=["smoke"])
        assert has_tag(snap, "smoke") is True

    def test_false_when_absent(self):
        snap = _make_snap(tags=[])
        assert has_tag(snap, "smoke") is False

    def test_false_when_no_tags_key(self):
        snap = _make_snap()
        assert has_tag(snap, "smoke") is False


class TestFilterByTags:
    def setup_method(self):
        self.snaps = [
            _make_snap(tags=["smoke", "regression"]),
            _make_snap(tags=["smoke"]),
            _make_snap(tags=["regression"]),
            _make_snap(tags=[]),
        ]

    def test_no_filters_returns_all(self):
        assert filter_by_tags(self.snaps) == self.snaps

    def test_include_single_tag(self):
        result = filter_by_tags(self.snaps, include=["smoke"])
        assert len(result) == 2

    def test_include_multiple_tags_requires_all(self):
        result = filter_by_tags(self.snaps, include=["smoke", "regression"])
        assert len(result) == 1

    def test_exclude_removes_matching(self):
        result = filter_by_tags(self.snaps, exclude=["regression"])
        assert all("regression" not in s.get("tags", []) for s in result)

    def test_include_and_exclude_combined(self):
        result = filter_by_tags(self.snaps, include=["smoke"], exclude=["regression"])
        assert len(result) == 1
        assert result[0]["tags"] == ["smoke"]


class TestListTags:
    def test_returns_sorted_unique_tags(self):
        snaps = [
            _make_snap(tags=["z", "a"]),
            _make_snap(tags=["a", "b"]),
        ]
        assert list_tags(snaps) == ["a", "b", "z"]

    def test_empty_when_no_tags(self):
        snaps = [_make_snap(), _make_snap()]
        assert list_tags(snaps) == []
