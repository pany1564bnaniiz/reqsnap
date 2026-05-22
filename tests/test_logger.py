"""Tests for reqsnap.logger module."""

import json
from unittest.mock import MagicMock, patch

import pytest

from reqsnap.logger import RequestSnapshot, capture


# ---------------------------------------------------------------------------
# RequestSnapshot unit tests
# ---------------------------------------------------------------------------

class TestRequestSnapshot:
    def test_to_dict_contains_required_keys(self):
        snap = RequestSnapshot(
            url="https://example.com/api",
            method="GET",
            status_code=200,
            response_body={"ok": True},
        )
        d = snap.to_dict()
        for key in ("url", "method", "status_code", "response_body", "timestamp", "environment"):
            assert key in d

    def test_to_json_is_valid_json(self):
        snap = RequestSnapshot(
            url="https://example.com",
            method="POST",
            status_code=201,
            response_body="created",
        )
        parsed = json.loads(snap.to_json())
        assert parsed["status_code"] == 201

    def test_default_environment_is_default(self):
        snap = RequestSnapshot(url="x", method="GET", status_code=200, response_body=None)
        assert snap.environment == "default"

    def test_custom_environment(self):
        snap = RequestSnapshot(
            url="x", method="GET", status_code=200, response_body=None, environment="staging"
        )
        assert snap.environment == "staging"


# ---------------------------------------------------------------------------
# capture() integration-style tests (requests mocked)
# ---------------------------------------------------------------------------

def _make_mock_response(status_code=200, json_data=None, text=""):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.request = MagicMock()
    mock_resp.request.headers = {"User-Agent": "reqsnap"}
    if json_data is not None:
        mock_resp.json.return_value = json_data
    else:
        mock_resp.json.side_effect = ValueError("no json")
        mock_resp.text = text
    return mock_resp


@patch("reqsnap.logger.requests.request")
def test_capture_returns_snapshot(mock_request):
    mock_request.return_value = _make_mock_response(json_data={"id": 1})
    snap = capture("https://api.example.com/items/1", environment="prod")
    assert isinstance(snap, RequestSnapshot)
    assert snap.status_code == 200
    assert snap.response_body == {"id": 1}
    assert snap.environment == "prod"
    assert snap.elapsed_ms >= 0


@patch("reqsnap.logger.requests.request")
def test_capture_falls_back_to_text(mock_request):
    mock_request.return_value = _make_mock_response(status_code=500, text="Internal Server Error")
    snap = capture("https://api.example.com/boom")
    assert snap.status_code == 500
    assert snap.response_body == "Internal Server Error"


@patch("reqsnap.logger.requests.request")
def test_capture_records_request_body(mock_request):
    mock_request.return_value = _make_mock_response(json_data={"created": True})
    payload = {"name": "test"}
    snap = capture("https://api.example.com/items", method="POST", json=payload)
    assert snap.method == "POST"
    assert snap.request_body == payload
