"""Tests for reqsnap.pin module."""

import pytest
from reqsnap.pin import (
    pin_snapshot,
    unpin_snapshot,
    is_pinned,
    filter_pinned,
    filter_unpinned,
    list_pinned_ids,
)


def _make_snap(url="https://api.example.com/v1", pinned=False, snap_id=None):
    snap = {"url": url, "method": "GET", "status_code": 200}
    if snap_id:
        snap["id"] = snap_id
    if pinned:
        snap["pinned"] = True
    return snap


class TestPinSnapshot:
    def test_sets_pinned_true(self):
        snap = _make_snap()
        result = pin_snapshot(snap)
        assert result["pinned"] is True

    def test_does_not_mutate_original(self):
        snap = _make_snap()
        pin_snapshot(snap)
        assert "pinned" not in snap

    def test_already_pinned_remains_pinned(self):
        snap = _make_snap(pinned=True)
        result = pin_snapshot(snap)
        assert result["pinned"] is True


class TestUnpinSnapshot:
    def test_removes_pinned_key(self):
        snap = _make_snap(pinned=True)
        result = unpin_snapshot(snap)
        assert "pinned" not in result

    def test_does_not_mutate_original(self):
        snap = _make_snap(pinned=True)
        unpin_snapshot(snap)
        assert snap["pinned"] is True

    def test_safe_on_unpinned_snapshot(self):
        snap = _make_snap()
        result = unpin_snapshot(snap)
        assert "pinned" not in result


class TestIsPinned:
    def test_returns_true_for_pinned(self):
        snap = _make_snap(pinned=True)
        assert is_pinned(snap) is True

    def test_returns_false_for_unpinned(self):
        snap = _make_snap()
        assert is_pinned(snap) is False

    def test_returns_false_when_key_missing(self):
        assert is_pinned({}) is False


class TestFilterPinned:
    def test_returns_only_pinned(self):
        snaps = [_make_snap(pinned=True), _make_snap(), _make_snap(pinned=True)]
        result = filter_pinned(snaps)
        assert len(result) == 2
        assert all(is_pinned(s) for s in result)

    def test_empty_list(self):
        assert filter_pinned([]) == []

    def test_none_pinned_returns_empty(self):
        snaps = [_make_snap(), _make_snap()]
        assert filter_pinned(snaps) == []


class TestFilterUnpinned:
    def test_returns_only_unpinned(self):
        snaps = [_make_snap(pinned=True), _make_snap(), _make_snap()]
        result = filter_unpinned(snaps)
        assert len(result) == 2


class TestListPinnedIds:
    def test_returns_ids_when_present(self):
        snaps = [_make_snap(pinned=True, snap_id="abc123"), _make_snap()]
        ids = list_pinned_ids(snaps)
        assert ids == ["abc123"]

    def test_falls_back_to_url(self):
        snaps = [_make_snap(url="https://api.example.com", pinned=True)]
        ids = list_pinned_ids(snaps)
        assert ids == ["https://api.example.com"]

    def test_empty_list(self):
        assert list_pinned_ids([]) == []
