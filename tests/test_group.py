"""Tests for reqsnap.group."""

import pytest
from reqsnap.group import (
    SUPPORTED_FIELDS,
    group_by,
    group_summary,
    largest_group,
)


def _make_snap(url="https://api.example.com", method="GET",
               status_code=200, environment="production"):
    return {
        "url": url,
        "method": method,
        "status_code": status_code,
        "environment": environment,
    }


SNAPS = [
    _make_snap(url="https://a.com", method="GET",  status_code=200, environment="prod"),
    _make_snap(url="https://b.com", method="POST", status_code=201, environment="prod"),
    _make_snap(url="https://c.com", method="GET",  status_code=404, environment="staging"),
    _make_snap(url="https://d.com", method="GET",  status_code=200, environment="staging"),
]


class TestGroupBy:
    def test_raises_on_unsupported_field(self):
        with pytest.raises(ValueError, match="Unsupported group field"):
            group_by(SNAPS, "body")

    def test_all_supported_fields_accepted(self):
        for field in SUPPORTED_FIELDS:
            result = group_by(SNAPS, field)
            assert isinstance(result, dict)

    def test_group_by_method(self):
        groups = group_by(SNAPS, "method")
        assert "GET" in groups
        assert "POST" in groups
        assert len(groups["GET"]) == 3
        assert len(groups["POST"]) == 1

    def test_group_by_environment(self):
        groups = group_by(SNAPS, "environment")
        assert set(groups.keys()) == {"prod", "staging"}

    def test_group_by_status_code(self):
        groups = group_by(SNAPS, "status_code")
        assert "200" in groups
        assert len(groups["200"]) == 2

    def test_empty_list_returns_empty_dict(self):
        assert group_by([], "method") == {}

    def test_missing_field_key_uses_empty_string(self):
        snaps = [{"method": "GET"}, {"method": "POST"}]  # no 'url'
        groups = group_by(snaps, "url")
        assert "" in groups
        assert len(groups[""] ) == 2


class TestGroupSummary:
    def test_returns_list(self):
        groups = group_by(SNAPS, "environment")
        result = group_summary(groups)
        assert isinstance(result, list)

    def test_each_entry_has_required_keys(self):
        groups = group_by(SNAPS, "method")
        for entry in group_summary(groups):
            assert "key" in entry
            assert "count" in entry
            assert "urls" in entry

    def test_count_is_correct(self):
        groups = group_by(SNAPS, "method")
        summary = {e["key"]: e["count"] for e in group_summary(groups)}
        assert summary["GET"] == 3
        assert summary["POST"] == 1

    def test_urls_are_deduplicated(self):
        snaps = [
            _make_snap(url="https://x.com", method="GET"),
            _make_snap(url="https://x.com", method="GET"),
        ]
        groups = group_by(snaps, "method")
        summary = group_summary(groups)
        assert summary[0]["urls"] == ["https://x.com"]

    def test_sorted_by_key(self):
        groups = group_by(SNAPS, "environment")
        keys = [e["key"] for e in group_summary(groups)]
        assert keys == sorted(keys)


class TestLargestGroup:
    def test_returns_key_of_largest(self):
        groups = group_by(SNAPS, "method")
        assert largest_group(groups) == "GET"

    def test_empty_groups_returns_empty_string(self):
        assert largest_group({}) == ""
