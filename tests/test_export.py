"""Tests for reqsnap.export module."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from reqsnap.export import export_diff, SUPPORTED_FORMATS


SAMPLE_DIFF_WITH_CHANGES = {
    "has_diff": True,
    "environment_a": "staging",
    "environment_b": "production",
    "changes": [
        {"key": "body.price", "value_a": 9.99, "value_b": 12.99},
        {"key": "status_code", "value_a": 200, "value_b": 201},
    ],
}

SAMPLE_DIFF_IDENTICAL = {
    "has_diff": False,
    "environment_a": "dev",
    "environment_b": "staging",
    "changes": [],
}


class TestExportDiff:
    def test_supported_formats_contains_expected(self):
        assert "json" in SUPPORTED_FORMATS
        assert "html" in SUPPORTED_FORMATS
        assert "markdown" in SUPPORTED_FORMATS

    def test_raises_on_unsupported_format(self):
        with pytest.raises(ValueError, match="Unsupported format"):
            export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="csv")

    # --- JSON ---
    def test_json_export_is_valid_json(self):
        result = export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="json")
        parsed = json.loads(result)
        assert parsed["has_diff"] is True

    def test_json_export_preserves_changes(self):
        result = export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="json")
        parsed = json.loads(result)
        assert len(parsed["changes"]) == 2

    def test_json_export_identical_diff(self):
        result = export_diff(SAMPLE_DIFF_IDENTICAL, fmt="json")
        parsed = json.loads(result)
        assert parsed["has_diff"] is False
        assert parsed["changes"] == []

    # --- HTML ---
    def test_html_export_returns_string(self):
        result = export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="html")
        assert isinstance(result, str)

    def test_html_export_contains_doctype(self):
        result = export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="html")
        assert "<!DOCTYPE html>" in result

    def test_html_export_contains_environment_names(self):
        result = export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="html")
        assert "staging" in result
        assert "production" in result

    def test_html_export_shows_differences_found(self):
        result = export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="html")
        assert "Differences Found" in result

    def test_html_export_shows_identical_when_no_diff(self):
        result = export_diff(SAMPLE_DIFF_IDENTICAL, fmt="html")
        assert "Identical" in result

    # --- Markdown ---
    def test_markdown_export_returns_string(self):
        result = export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="markdown")
        assert isinstance(result, str)

    def test_markdown_export_contains_header(self):
        result = export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="markdown")
        assert "# reqsnap Diff Report" in result

    def test_markdown_export_contains_environment_names(self):
        result = export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="markdown")
        assert "staging" in result
        assert "production" in result

    def test_markdown_export_shows_diff_status(self):
        result = export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="markdown")
        assert "Differences Found" in result

    def test_markdown_export_identical_status(self):
        result = export_diff(SAMPLE_DIFF_IDENTICAL, fmt="markdown")
        assert "Identical" in result

    def test_markdown_export_no_changes_note(self):
        result = export_diff(SAMPLE_DIFF_IDENTICAL, fmt="markdown")
        assert "No differences detected" in result

    # --- File output ---
    def test_writes_to_file_when_path_given(self, tmp_path):
        out = tmp_path / "report.json"
        export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="json", output_path=out)
        assert out.exists()
        parsed = json.loads(out.read_text())
        assert "has_diff" in parsed

    def test_html_written_to_file(self, tmp_path):
        out = tmp_path / "report.html"
        export_diff(SAMPLE_DIFF_WITH_CHANGES, fmt="html", output_path=out)
        assert out.exists()
        assert "<!DOCTYPE html>" in out.read_text()
