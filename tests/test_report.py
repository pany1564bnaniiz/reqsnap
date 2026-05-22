"""Tests for reqsnap.report module."""

import pytest
from reqsnap.report import format_diff_report


IDENTICAL_DIFF = {
    "environment_a": "staging",
    "environment_b": "production",
    "url": "https://api.example.com/items",
    "method": "GET",
    "has_diff": False,
    "status_code": {"differs": False, "a": 200, "b": 200},
    "body": {"differs": False, "changes": []},
    "headers": {"differs": False, "changes": []},
}

BODY_DIFF = {
    "environment_a": "staging",
    "environment_b": "production",
    "url": "https://api.example.com/items",
    "method": "GET",
    "has_diff": True,
    "status_code": {"differs": False, "a": 200, "b": 200},
    "body": {
        "differs": True,
        "changes": [
            {"key": "name", "a": "Alice", "b": "Bob"},
        ],
    },
    "headers": {"differs": False, "changes": []},
}

STATUS_DIFF = {
    "environment_a": "dev",
    "environment_b": "prod",
    "url": "https://api.example.com/health",
    "method": "GET",
    "has_diff": True,
    "status_code": {"differs": True, "a": 200, "b": 503},
    "body": {"differs": False, "changes": []},
    "headers": {"differs": False, "changes": []},
}


class TestFormatDiffReport:
    def test_returns_string(self):
        report = format_diff_report(IDENTICAL_DIFF)
        assert isinstance(report, str)

    def test_contains_environment_names(self):
        report = format_diff_report(IDENTICAL_DIFF, use_color=False)
        assert "staging" in report
        assert "production" in report

    def test_identical_shows_identical_status(self):
        report = format_diff_report(IDENTICAL_DIFF, use_color=False)
        assert "IDENTICAL" in report

    def test_diff_shows_differences_found(self):
        report = format_diff_report(BODY_DIFF, use_color=False)
        assert "DIFFERENCES FOUND" in report

    def test_body_changes_shown(self):
        report = format_diff_report(BODY_DIFF, use_color=False)
        assert ".name" in report
        assert "Alice" in report
        assert "Bob" in report

    def test_status_code_change_shown(self):
        report = format_diff_report(STATUS_DIFF, use_color=False)
        assert "Status Code" in report
        assert "503" in report

    def test_url_included_in_report(self):
        report = format_diff_report(BODY_DIFF, use_color=False)
        assert "https://api.example.com/items" in report

    def test_no_color_mode_has_no_ansi_codes(self):
        report = format_diff_report(BODY_DIFF, use_color=False)
        assert "\033[" not in report

    def test_color_mode_includes_ansi_codes(self):
        report = format_diff_report(BODY_DIFF, use_color=True)
        assert "\033[" in report

    def test_report_ends_with_separator(self):
        report = format_diff_report(IDENTICAL_DIFF, use_color=False)
        assert report.strip().endswith("=" * 40)
