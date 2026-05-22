"""Tests for reqsnap.replay module."""

import json
import unittest
from unittest.mock import MagicMock, patch
from io import BytesIO
import http.client

from reqsnap.replay import _build_request, replay_snapshot, replay_to_json


SAMPLE_SNAPSHOT = {
    "id": "abc123",
    "url": "https://example.com/api/users",
    "method": "GET",
    "request_headers": {"Accept": "application/json"},
    "request_body": None,
    "response_status": 200,
    "response_headers": {"Content-Type": "application/json"},
    "response_body": '{"users": []}',
    "elapsed_ms": 45.0,
    "environment": "production",
    "timestamp": "2024-01-01T00:00:00",
}


class TestBuildRequest(unittest.TestCase):
    def test_uses_snapshot_url(self):
        req = _build_request(SAMPLE_SNAPSHOT)
        self.assertEqual(req.full_url, SAMPLE_SNAPSHOT["url"])

    def test_override_url_is_used(self):
        req = _build_request(SAMPLE_SNAPSHOT, override_url="https://staging.example.com/api/users")
        self.assertIn("staging", req.full_url)

    def test_method_is_preserved(self):
        req = _build_request(SAMPLE_SNAPSHOT)
        self.assertEqual(req.get_method(), "GET")

    def test_headers_are_set(self):
        req = _build_request(SAMPLE_SNAPSHOT)
        self.assertIn("Accept", req.headers)


class TestReplaySnapshot(unittest.TestCase):
    def _make_mock_response(self, status=200, body=b'{"ok": true}'):
        mock_resp = MagicMock()
        mock_resp.status = status
        mock_resp.read.return_value = body
        mock_resp.headers = {"Content-Type": "application/json"}
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    @patch("reqsnap.replay.load_snapshot", return_value=SAMPLE_SNAPSHOT)
    @patch("reqsnap.replay.urllib.request.urlopen")
    def test_returns_dict_with_required_keys(self, mock_urlopen, mock_load):
        mock_urlopen.return_value = self._make_mock_response()
        result = replay_snapshot("abc123")
        for key in ("url", "method", "response_status", "environment", "elapsed_ms"):
            self.assertIn(key, result)

    @patch("reqsnap.replay.load_snapshot", return_value=SAMPLE_SNAPSHOT)
    @patch("reqsnap.replay.urllib.request.urlopen")
    def test_environment_is_set(self, mock_urlopen, mock_load):
        mock_urlopen.return_value = self._make_mock_response()
        result = replay_snapshot("abc123", environment="staging")
        self.assertEqual(result["environment"], "staging")

    @patch("reqsnap.replay.load_snapshot", return_value=SAMPLE_SNAPSHOT)
    @patch("reqsnap.replay.urllib.request.urlopen")
    def test_response_status_captured(self, mock_urlopen, mock_load):
        mock_urlopen.return_value = self._make_mock_response(status=404)
        result = replay_snapshot("abc123")
        self.assertEqual(result["response_status"], 404)

    @patch("reqsnap.replay.load_snapshot", return_value=SAMPLE_SNAPSHOT)
    @patch("reqsnap.replay.urllib.request.urlopen")
    def test_replay_to_json_is_valid_json(self, mock_urlopen, mock_load):
        mock_urlopen.return_value = self._make_mock_response()
        result = replay_to_json("abc123")
        parsed = json.loads(result)
        self.assertIsInstance(parsed, dict)


if __name__ == "__main__":
    unittest.main()
