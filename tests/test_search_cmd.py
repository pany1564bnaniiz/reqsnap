"""Tests for the search CLI command handler."""

import json
import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from reqsnap.commands.search_cmd import handle_search, register_parser


SAMPLE_SNAP = {
    "url": "https://api.example.com/users",
    "method": "GET",
    "environment": "production",
    "response": {"status_code": 200, "body": {"users": []}},
    "_source_file": "snap_001.json",
}


def _make_args(**kwargs):
    defaults = {
        "query": "example",
        "field": None,
        "case_sensitive": False,
        "json": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


class TestHandleSearch:
    @patch("reqsnap.commands.search_cmd._snapshot_dir")
    @patch("reqsnap.commands.search_cmd.search_snapshots")
    def test_prints_match_count(self, mock_search, mock_dir, tmp_path, capsys):
        mock_dir.return_value = tmp_path
        (tmp_path / "snap_001.json").write_text("{}")
        mock_search.return_value = [SAMPLE_SNAP]

        handle_search(_make_args(query="example"))

        captured = capsys.readouterr()
        assert "1 matching" in captured.out

    @patch("reqsnap.commands.search_cmd._snapshot_dir")
    @patch("reqsnap.commands.search_cmd.search_snapshots")
    def test_prints_url_and_method(self, mock_search, mock_dir, tmp_path, capsys):
        mock_dir.return_value = tmp_path
        (tmp_path / "snap_001.json").write_text("{}")
        mock_search.return_value = [SAMPLE_SNAP]

        handle_search(_make_args(query="example"))

        captured = capsys.readouterr()
        assert "https://api.example.com/users" in captured.out
        assert "GET" in captured.out

    @patch("reqsnap.commands.search_cmd._snapshot_dir")
    def test_no_directory_warns_user(self, mock_dir, tmp_path, capsys):
        missing = tmp_path / "nonexistent"
        mock_dir.return_value = missing

        handle_search(_make_args(query="anything"))

        captured = capsys.readouterr()
        assert "No snapshots directory" in captured.out

    @patch("reqsnap.commands.search_cmd._snapshot_dir")
    @patch("reqsnap.commands.search_cmd.search_snapshots")
    def test_no_results_shows_message(self, mock_search, mock_dir, tmp_path, capsys):
        mock_dir.return_value = tmp_path
        (tmp_path / "snap_001.json").write_text("{}")
        mock_search.return_value = []

        handle_search(_make_args(query="notfound"))

        captured = capsys.readouterr()
        assert "No snapshots matched" in captured.out

    @patch("reqsnap.commands.search_cmd._snapshot_dir")
    @patch("reqsnap.commands.search_cmd.search_snapshots")
    def test_json_flag_outputs_valid_json(self, mock_search, mock_dir, tmp_path, capsys):
        mock_dir.return_value = tmp_path
        (tmp_path / "snap_001.json").write_text("{}")
        mock_search.return_value = [SAMPLE_SNAP]

        handle_search(_make_args(query="example", json=True))

        captured = capsys.readouterr()
        json_start = captured.out.index("[")
        parsed = json.loads(captured.out[json_start:])
        assert isinstance(parsed, list)
        assert "_source_file" not in parsed[0]


class TestRegisterParser:
    def test_registers_search_subcommand(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parser(subparsers)
        args = parser.parse_args(["search", "hello"])
        assert args.query == "hello"

    def test_field_option_defaults_to_none(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parser(subparsers)
        args = parser.parse_args(["search", "test"])
        assert args.field is None

    def test_case_sensitive_flag(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parser(subparsers)
        args = parser.parse_args(["search", "test", "--case-sensitive"])
        assert args.case_sensitive is True
