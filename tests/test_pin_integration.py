"""Integration tests: pin a snapshot, then diff against it as a baseline."""

import json
from pathlib import Path

import pytest

from reqsnap.pin import pin_snapshot, is_pinned, filter_pinned
from reqsnap.diff import diff_snapshots


def _make_snap(url="https://api.example.com", body=None, status=200, env="production"):
    return {
        "url": url,
        "method": "GET",
        "status_code": status,
        "body": body or {"result": "ok"},
        "headers": {"content-type": "application/json"},
        "environment": env,
    }


class TestPinAndDiffIntegration:
    def test_pinned_snapshot_used_as_baseline(self):
        baseline = pin_snapshot(_make_snap(body={"version": 1}))
        current = _make_snap(body={"version": 2})
        assert is_pinned(baseline)
        result = diff_snapshots(baseline, current)
        assert result["has_diff"] is True

    def test_pinned_identical_snapshot_shows_no_diff(self):
        baseline = pin_snapshot(_make_snap(body={"version": 1}))
        current = _make_snap(body={"version": 1})
        result = diff_snapshots(baseline, current)
        assert result["has_diff"] is False

    def test_only_pinned_selected_from_pool(self):
        pool = [
            pin_snapshot(_make_snap(url="https://api.example.com/a")),
            _make_snap(url="https://api.example.com/b"),
            pin_snapshot(_make_snap(url="https://api.example.com/c")),
        ]
        pinned = filter_pinned(pool)
        assert len(pinned) == 2
        urls = [s["url"] for s in pinned]
        assert "https://api.example.com/a" in urls
        assert "https://api.example.com/c" in urls

    def test_unpin_then_diff_still_works(self):
        from reqsnap.pin import unpin_snapshot
        baseline = pin_snapshot(_make_snap())
        unpinned = unpin_snapshot(baseline)
        assert not is_pinned(unpinned)
        result = diff_snapshots(unpinned, _make_snap())
        assert result["has_diff"] is False

    def test_pin_preserves_all_existing_fields(self):
        snap = _make_snap()
        snap["tags"] = ["v1", "stable"]
        pinned = pin_snapshot(snap)
        assert pinned["tags"] == ["v1", "stable"]
        assert pinned["url"] == snap["url"]
        assert pinned["body"] == snap["body"]
