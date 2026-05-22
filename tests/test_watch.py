"""Tests for reqsnap.watch module."""

import pytest
from unittest.mock import patch, MagicMock

from reqsnap.watch import watch, watch_to_json


def _make_mock_response(status: int = 200, body: str = '{"ok": true}') -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.url = "https://example.com/api"
    resp.headers = {"Content-Type": "application/json"}
    resp.text = body
    resp.elapsed.total_seconds.return_value = 0.1
    resp.request.method = "GET"
    return resp


class TestWatch:
    def test_on_change_called_on_initial(self):
        changes = []
        mock_resp = _make_mock_response()

        with patch("reqsnap.watch.requests.request", return_value=mock_resp), \
             patch("reqsnap.watch.time.sleep"):
            watch(
                url="https://example.com/api",
                max_iterations=1,
                on_change=lambda d: changes.append(d),
            )

        assert len(changes) == 1
        assert changes[0]["initial"] is True
        assert changes[0]["has_diff"] is False

    def test_on_change_called_when_body_differs(self):
        changes = []
        responses = [
            _make_mock_response(body='{"ok": true}'),
            _make_mock_response(body='{"ok": false}'),
        ]

        with patch("reqsnap.watch.requests.request", side_effect=responses), \
             patch("reqsnap.watch.time.sleep"):
            watch(
                url="https://example.com/api",
                max_iterations=2,
                on_change=lambda d: changes.append(d),
            )

        assert len(changes) == 2
        diff_change = changes[1]
        assert diff_change["has_diff"] is True

    def test_no_change_does_not_call_on_change_twice(self):
        changes = []
        body = '{"status": "ok"}'
        responses = [
            _make_mock_response(body=body),
            _make_mock_response(body=body),
        ]

        with patch("reqsnap.watch.requests.request", side_effect=responses), \
             patch("reqsnap.watch.time.sleep"):
            watch(
                url="https://example.com/api",
                max_iterations=2,
                on_change=lambda d: changes.append(d),
            )

        # initial + second poll with no diff — on_change still called for initial
        diff_calls = [c for c in changes if not c.get("initial")]
        assert all(not c["has_diff"] for c in diff_calls)

    def test_save_calls_save_snapshot(self):
        mock_resp = _make_mock_response()

        with patch("reqsnap.watch.requests.request", return_value=mock_resp), \
             patch("reqsnap.watch.time.sleep"), \
             patch("reqsnap.watch.save_snapshot") as mock_save:
            watch(
                url="https://example.com/api",
                max_iterations=1,
                save=True,
            )

        mock_save.assert_called_once()

    def test_watch_to_json_returns_string(self):
        diff = {"has_diff": True, "changes": []}
        result = watch_to_json(diff)
        import json
        parsed = json.loads(result)
        assert parsed["has_diff"] is True
