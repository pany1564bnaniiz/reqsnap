"""Tests for reqsnap.compare module."""

import pytest
from reqsnap.compare import compare_snapshots, summarize_comparison


def _make_snap(env="prod", body=None, status=200, url="https://example.com/api"):
    return {
        "environment": env,
        "url": url,
        "method": "GET",
        "status_code": status,
        "headers": {"content-type": "application/json"},
        "body": body or {"key": "value"},
    }


class TestCompareSnapshots:
    def test_raises_with_fewer_than_two_snapshots(self):
        with pytest.raises(ValueError, match="At least two"):
            compare_snapshots([_make_snap()])

    def test_returns_required_keys(self):
        report = compare_snapshots([_make_snap(), _make_snap()])
        assert "total" in report
        assert "differing" in report
        assert "identical" in report
        assert "comparisons" in report

    def test_identical_snapshots_count(self):
        report = compare_snapshots([_make_snap(), _make_snap()])
        assert report["identical"] == 1
        assert report["differing"] == 0

    def test_differing_snapshots_count(self):
        snap_a = _make_snap(body={"key": "value"})
        snap_b = _make_snap(body={"key": "other"})
        report = compare_snapshots([snap_a, snap_b])
        assert report["differing"] == 1
        assert report["identical"] == 0

    def test_multiple_pairs(self):
        snaps = [_make_snap(env=f"env{i}") for i in range(3)]
        report = compare_snapshots(snaps)
        assert report["total"] == 2
        assert len(report["comparisons"]) == 2

    def test_only_diffs_filters_identical(self):
        snap_a = _make_snap(body={"k": "v"})
        snap_b = _make_snap(body={"k": "v"})
        snap_c = _make_snap(body={"k": "different"})
        report = compare_snapshots([snap_a, snap_b, snap_c], only_diffs=True)
        assert report["total"] == 1
        assert report["differing"] == 1

    def test_ignore_keys_excludes_field(self):
        snap_a = _make_snap(body={"key": "value", "ts": "2024-01-01"})
        snap_b = _make_snap(body={"key": "value", "ts": "2024-06-01"})
        report = compare_snapshots([snap_a, snap_b], ignore_keys=["ts"])
        assert report["identical"] == 1
        assert report["differing"] == 0


class TestSummarizeComparison:
    def test_returns_string(self):
        report = compare_snapshots([_make_snap(), _make_snap()])
        result = summarize_comparison(report)
        assert isinstance(result, str)

    def test_contains_totals(self):
        report = compare_snapshots([_make_snap(), _make_snap()])
        summary = summarize_comparison(report)
        assert "Comparisons" in summary
        assert "Identical" in summary
        assert "Differing" in summary

    def test_shows_same_status_for_identical(self):
        report = compare_snapshots([_make_snap(), _make_snap()])
        summary = summarize_comparison(report)
        assert "SAME" in summary

    def test_shows_diff_status_for_differing(self):
        snap_a = _make_snap(body={"a": 1})
        snap_b = _make_snap(body={"a": 2})
        report = compare_snapshots([snap_a, snap_b])
        summary = summarize_comparison(report)
        assert "DIFF" in summary
