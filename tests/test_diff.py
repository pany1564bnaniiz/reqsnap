"""Tests for the reqsnap.diff module."""

import json
import pytest

from reqsnap.diff import (
    diff_snapshots,
    diff_bodies,
    diff_to_json,
    DIFF_ADDED,
    DIFF_REMOVED,
    DIFF_CHANGED,
    DIFF_UNCHANGED,
)


SNAPSHOT_A = {
    "url": "https://api.example.com/users",
    "method": "GET",
    "status_code": 200,
    "environment": "staging",
    "body": {"count": 10, "page": 1},
}

SNAPSHOT_B = {
    "url": "https://api.example.com/users",
    "method": "GET",
    "status_code": 200,
    "environment": "production",
    "body": {"count": 12, "page": 1},
}


class TestDiffSnapshots:
    def test_returns_dict_with_required_keys(self):
        result = diff_snapshots(SNAPSHOT_A, SNAPSHOT_B)
        assert "environment_a" in result
        assert "environment_b" in result
        assert "has_diff" in result
        assert "diffs" in result

    def test_has_diff_true_when_bodies_differ(self):
        result = diff_snapshots(SNAPSHOT_A, SNAPSHOT_B)
        assert result["has_diff"] is True

    def test_has_diff_false_when_identical(self):
        result = diff_snapshots(SNAPSHOT_A, SNAPSHOT_A)
        assert result["has_diff"] is False

    def test_environment_labels_are_correct(self):
        result = diff_snapshots(SNAPSHOT_A, SNAPSHOT_B)
        assert result["environment_a"] == "staging"
        assert result["environment_b"] == "production"

    def test_changed_status_code_detected(self):
        snap_b = {**SNAPSHOT_B, "status_code": 404}
        result = diff_snapshots(SNAPSHOT_A, snap_b)
        changed = [d for d in result["diffs"] if d["key"] == "status_code"]
        assert len(changed) == 1
        assert changed[0]["status"] == DIFF_CHANGED


class TestDiffBodies:
    def test_added_key(self):
        diffs = diff_bodies({"a": 1}, {"a": 1, "b": 2})
        added = [d for d in diffs if d["status"] == DIFF_ADDED]
        assert any(d["key"] == "body.b" for d in added)

    def test_removed_key(self):
        diffs = diff_bodies({"a": 1, "b": 2}, {"a": 1})
        removed = [d for d in diffs if d["status"] == DIFF_REMOVED]
        assert any(d["key"] == "body.b" for d in removed)

    def test_changed_value(self):
        diffs = diff_bodies({"count": 10}, {"count": 20})
        assert diffs[0]["status"] == DIFF_CHANGED
        assert diffs[0]["left"] == 10
        assert diffs[0]["right"] == 20

    def test_unchanged_value(self):
        diffs = diff_bodies({"page": 1}, {"page": 1})
        assert diffs[0]["status"] == DIFF_UNCHANGED

    def test_non_dict_bodies(self):
        diffs = diff_bodies("text response", "different text")
        assert diffs[0]["status"] == DIFF_CHANGED

    def test_identical_non_dict_bodies(self):
        diffs = diff_bodies("same", "same")
        assert diffs == []


class TestDiffToJson:
    def test_output_is_valid_json(self):
        result = diff_snapshots(SNAPSHOT_A, SNAPSHOT_B)
        output = diff_to_json(result)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_json_contains_has_diff(self):
        result = diff_snapshots(SNAPSHOT_A, SNAPSHOT_B)
        output = diff_to_json(result)
        parsed = json.loads(output)
        assert "has_diff" in parsed
