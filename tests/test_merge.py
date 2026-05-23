"""Tests for reqsnap.merge module."""

import pytest
from reqsnap.merge import merge_snapshots, merge_summary


def _make_snap(url="https://api.example.com", method="GET", status=200,
               body="{}", env="production"):
    return {
        "url": url,
        "method": method,
        "status_code": status,
        "body": body,
        "environment": env,
        "headers": {"Content-Type": "application/json"},
    }


class TestMergeSnapshots:
    def test_raises_on_empty_list(self):
        with pytest.raises(ValueError, match="empty"):
            merge_snapshots([])

    def test_raises_on_unsupported_strategy(self):
        snaps = [_make_snap()]
        with pytest.raises(ValueError, match="Unsupported strategy"):
            merge_snapshots(snaps, strategy="random")

    def test_latest_strategy_uses_last_snapshot(self):
        snaps = [
            _make_snap(status=200),
            _make_snap(status=404),
            _make_snap(status=500),
        ]
        result = merge_snapshots(snaps, strategy="latest")
        assert result["status_code"] == 500

    def test_first_strategy_uses_first_snapshot(self):
        snaps = [
            _make_snap(status=200),
            _make_snap(status=404),
        ]
        result = merge_snapshots(snaps, strategy="first")
        assert result["status_code"] == 200

    def test_majority_strategy_picks_most_common(self):
        snaps = [
            _make_snap(status=200),
            _make_snap(status=200),
            _make_snap(status=404),
        ]
        result = merge_snapshots(snaps, strategy="majority")
        assert result["status_code"] == 200

    def test_merged_flag_is_set(self):
        snaps = [_make_snap(), _make_snap()]
        result = merge_snapshots(snaps)
        assert result["merged"] is True

    def test_merged_count_is_correct(self):
        snaps = [_make_snap() for _ in range(5)]
        result = merge_snapshots(snaps)
        assert result["merged_count"] == 5

    def test_merge_strategy_is_recorded(self):
        snaps = [_make_snap()]
        result = merge_snapshots(snaps, strategy="first")
        assert result["merge_strategy"] == "first"

    def test_single_snapshot_returns_itself(self):
        snap = _make_snap(url="https://single.example.com")
        result = merge_snapshots([snap], strategy="latest")
        assert result["url"] == "https://single.example.com"

    def test_majority_carries_over_extra_keys(self):
        snap = _make_snap()
        snap["custom_field"] = "custom_value"
        result = merge_snapshots([snap], strategy="majority")
        assert result.get("custom_field") == "custom_value"


class TestMergeSummary:
    def test_returns_string(self):
        snap = _make_snap()
        merged = merge_snapshots([snap, snap])
        summary = merge_summary(merged)
        assert isinstance(summary, str)

    def test_contains_count(self):
        snaps = [_make_snap() for _ in range(3)]
        merged = merge_snapshots(snaps)
        assert "3" in merge_summary(merged)

    def test_contains_strategy(self):
        snaps = [_make_snap()]
        merged = merge_snapshots(snaps, strategy="majority")
        assert "majority" in merge_summary(merged)

    def test_contains_url_and_method(self):
        snap = _make_snap(url="https://api.test.com/v1", method="POST")
        merged = merge_snapshots([snap])
        summary = merge_summary(merged)
        assert "https://api.test.com/v1" in summary
        assert "POST" in summary
