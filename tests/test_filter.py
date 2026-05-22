"""Tests for reqsnap.filter module."""

import pytest
from reqsnap.filter import filter_snapshots


SAMPLE_SNAPSHOTS = [
    {
        "url": "https://api.example.com/users",
        "method": "GET",
        "status_code": 200,
        "environment": "production",
    },
    {
        "url": "https://api.example.com/users/42",
        "method": "DELETE",
        "status_code": 404,
        "environment": "staging",
    },
    {
        "url": "https://api.example.com/orders",
        "method": "POST",
        "status_code": 201,
        "environment": "production",
    },
    {
        "url": "https://dev.internal/health",
        "method": "GET",
        "status_code": 200,
        "environment": "development",
    },
]


class TestFilterSnapshots:
    def test_no_filters_returns_all(self):
        result = filter_snapshots(SAMPLE_SNAPSHOTS)
        assert result == SAMPLE_SNAPSHOTS

    def test_filter_by_status_code(self):
        result = filter_snapshots(SAMPLE_SNAPSHOTS, status=200)
        assert len(result) == 2
        assert all(s["status_code"] == 200 for s in result)

    def test_filter_by_environment_case_insensitive(self):
        result = filter_snapshots(SAMPLE_SNAPSHOTS, environment="Production")
        assert len(result) == 2
        assert all(s["environment"] == "production" for s in result)

    def test_filter_by_url_pattern(self):
        result = filter_snapshots(SAMPLE_SNAPSHOTS, url_pattern="users")
        assert len(result) == 2

    def test_filter_by_method(self):
        result = filter_snapshots(SAMPLE_SNAPSHOTS, method="get")
        assert len(result) == 2
        assert all(s["method"] == "GET" for s in result)

    def test_combined_filters(self):
        result = filter_snapshots(
            SAMPLE_SNAPSHOTS, status=200, environment="production"
        )
        assert len(result) == 1
        assert result[0]["url"] == "https://api.example.com/users"

    def test_custom_filter(self):
        result = filter_snapshots(
            SAMPLE_SNAPSHOTS,
            custom=lambda s: s["status_code"] >= 400,
        )
        assert len(result) == 1
        assert result[0]["status_code"] == 404

    def test_no_match_returns_empty_list(self):
        result = filter_snapshots(SAMPLE_SNAPSHOTS, status=500)
        assert result == []

    def test_empty_input_returns_empty(self):
        result = filter_snapshots([], status=200, environment="production")
        assert result == []

    def test_url_pattern_case_insensitive(self):
        result = filter_snapshots(SAMPLE_SNAPSHOTS, url_pattern="HEALTH")
        assert len(result) == 1
        assert "health" in result[0]["url"]

    def test_method_filter_post(self):
        result = filter_snapshots(SAMPLE_SNAPSHOTS, method="POST")
        assert len(result) == 1
        assert result[0]["status_code"] == 201
