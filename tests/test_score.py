"""Tests for reqsnap.score."""

from __future__ import annotations

import pytest

from reqsnap.score import score_snapshot, score_details, rank_snapshots


def _make_snap(**kwargs):
    base = {
        "url": "https://example.com/api",
        "method": "GET",
        "status_code": 200,
        "response_body": '{"ok": true}',
        "response_headers": {"content-type": "application/json"},
        "environment": "production",
    }
    base.update(kwargs)
    return base


class TestScoreSnapshot:
    def test_perfect_snapshot_scores_below_or_equal_one(self):
        snap = _make_snap(
            pinned=True,
            tags=["smoke"],
            annotations=[{"note": "baseline"}],
            alias="prod-baseline",
        )
        result = score_snapshot(snap)
        assert 0.0 <= result <= 1.0

    def test_empty_snapshot_scores_zero(self):
        result = score_snapshot({})
        assert result == 0.0

    def test_status_ok_adds_to_score(self):
        good = _make_snap(status_code=200)
        bad = _make_snap(status_code=500)
        assert score_snapshot(good) > score_snapshot(bad)

    def test_pinned_adds_to_score(self):
        unpinned = _make_snap()
        pinned = _make_snap(pinned=True)
        assert score_snapshot(pinned) > score_snapshot(unpinned)

    def test_tags_add_to_score(self):
        without = _make_snap()
        with_tags = _make_snap(tags=["regression"])
        assert score_snapshot(with_tags) > score_snapshot(without)

    def test_alias_adds_to_score(self):
        without = _make_snap()
        with_alias = _make_snap(alias="my-snap")
        assert score_snapshot(with_alias) > score_snapshot(without)

    def test_score_is_float(self):
        result = score_snapshot(_make_snap())
        assert isinstance(result, float)


class TestScoreDetails:
    def test_returns_score_key(self):
        details = score_details(_make_snap())
        assert "score" in details

    def test_returns_breakdown_key(self):
        details = score_details(_make_snap())
        assert "breakdown" in details

    def test_breakdown_contains_all_criteria(self):
        details = score_details(_make_snap())
        expected = {
            "has_body", "has_headers", "status_ok",
            "is_pinned", "has_tags", "has_annotation", "has_alias",
        }
        assert set(details["breakdown"].keys()) == expected

    def test_breakdown_values_are_non_negative(self):
        details = score_details(_make_snap())
        for v in details["breakdown"].values():
            assert v >= 0.0


class TestRankSnapshots:
    def test_returns_list(self):
        snaps = [_make_snap(), _make_snap(status_code=404)]
        result = rank_snapshots(snaps)
        assert isinstance(result, list)

    def test_descending_order_by_default(self):
        snaps = [
            _make_snap(status_code=404),
            _make_snap(status_code=200, pinned=True, tags=["a"]),
            _make_snap(status_code=200),
        ]
        ranked = rank_snapshots(snaps)
        scores = [s["_score"] for s in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_ascending_order_when_requested(self):
        snaps = [_make_snap(status_code=200, pinned=True), _make_snap(status_code=500)]
        ranked = rank_snapshots(snaps, descending=False)
        scores = [s["_score"] for s in ranked]
        assert scores == sorted(scores)

    def test_score_key_added_to_each_item(self):
        snaps = [_make_snap(), _make_snap()]
        for item in rank_snapshots(snaps):
            assert "_score" in item

    def test_empty_list_returns_empty(self):
        assert rank_snapshots([]) == []
