"""Tests for reqsnap.validate module."""

import pytest
from reqsnap.validate import validate_snapshot, validate_all, REQUIRED_KEYS


def _make_snap(**overrides):
    base = {
        "url": "https://api.example.com/users",
        "method": "GET",
        "status_code": 200,
        "headers": {"Content-Type": "application/json"},
        "body": '{"id": 1}',
        "timestamp": "2024-01-01T00:00:00Z",
        "environment": "production",
    }
    base.update(overrides)
    return base


class TestValidateSnapshot:
    def test_valid_snapshot_returns_valid_true(self):
        result = validate_snapshot(_make_snap())
        assert result["valid"] is True
        assert result["errors"] == []

    def test_missing_key_returns_valid_false(self):
        snap = _make_snap()
        del snap["url"]
        result = validate_snapshot(snap)
        assert result["valid"] is False
        assert any("url" in e for e in result["errors"])

    def test_multiple_missing_keys_reported_together(self):
        snap = _make_snap()
        del snap["url"]
        del snap["method"]
        result = validate_snapshot(snap)
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert "url" in result["errors"][0]
        assert "method" in result["errors"][0]

    def test_invalid_status_code_type(self):
        result = validate_snapshot(_make_snap(status_code="200"))
        assert result["valid"] is False
        assert any("status_code" in e for e in result["errors"])

    def test_status_code_out_of_range(self):
        result = validate_snapshot(_make_snap(status_code=999))
        assert result["valid"] is False
        assert any("999" in e for e in result["errors"])

    def test_status_code_lower_boundary(self):
        assert validate_snapshot(_make_snap(status_code=100))["valid"] is True

    def test_status_code_upper_boundary(self):
        assert validate_snapshot(_make_snap(status_code=599))["valid"] is True

    def test_invalid_method(self):
        result = validate_snapshot(_make_snap(method="FETCH"))
        assert result["valid"] is False
        assert any("FETCH" in e for e in result["errors"])

    def test_method_case_insensitive_check(self):
        result = validate_snapshot(_make_snap(method="get"))
        assert result["valid"] is True

    def test_headers_not_dict(self):
        result = validate_snapshot(_make_snap(headers="Content-Type: application/json"))
        assert result["valid"] is False
        assert any("headers" in e for e in result["errors"])

    def test_multiple_field_errors_accumulated(self):
        result = validate_snapshot(_make_snap(status_code=999, method="BOGUS"))
        assert result["valid"] is False
        assert len(result["errors"]) >= 2


class TestValidateAll:
    def test_returns_list_with_index(self):
        snaps = [_make_snap(), _make_snap(url="https://other.com")]
        results = validate_all(snaps)
        assert len(results) == 2
        assert results[0]["index"] == 0
        assert results[1]["index"] == 1

    def test_empty_list_returns_empty(self):
        assert validate_all([]) == []

    def test_invalid_snap_flagged_in_batch(self):
        snaps = [_make_snap(), _make_snap(status_code=0)]
        results = validate_all(snaps)
        assert results[0]["valid"] is True
        assert results[1]["valid"] is False
