"""Replay captured HTTP snapshots against a target environment."""

import json
import time
from typing import Optional

import urllib.request
import urllib.error

from reqsnap.logger import capture
from reqsnap.storage import load_snapshot


def _build_request(snapshot: dict, override_url: Optional[str] = None):
    """Build a urllib Request from a snapshot dict."""
    url = override_url or snapshot["url"]
    method = snapshot.get("method", "GET").upper()
    headers = snapshot.get("request_headers", {})
    body = snapshot.get("request_body")

    data = body.encode() if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, method=method)
    for key, value in headers.items():
        req.add_header(key, value)
    return req


def replay_snapshot(
    snapshot_id: str,
    environment: str = "replayed",
    override_url: Optional[str] = None,
    timeout: int = 10,
) -> dict:
    """Replay a stored snapshot and return a new captured snapshot dict."""
    original = load_snapshot(snapshot_id)
    req = _build_request(original, override_url=override_url)

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            elapsed = round((time.time() - start) * 1000, 2)
            body = response.read().decode(errors="replace")
            status_code = response.status
            resp_headers = dict(response.headers)
    except urllib.error.HTTPError as exc:
        elapsed = round((time.time() - start) * 1000, 2)
        body = exc.read().decode(errors="replace")
        status_code = exc.code
        resp_headers = dict(exc.headers)

    return capture(
        url=req.full_url,
        method=req.get_method(),
        request_headers=dict(req.headers),
        request_body=original.get("request_body"),
        response_status=status_code,
        response_headers=resp_headers,
        response_body=body,
        elapsed_ms=elapsed,
        environment=environment,
    )


def replay_to_json(snapshot_id: str, **kwargs) -> str:
    """Replay a snapshot and return the result as a JSON string."""
    result = replay_snapshot(snapshot_id, **kwargs)
    return json.dumps(result, indent=2)
