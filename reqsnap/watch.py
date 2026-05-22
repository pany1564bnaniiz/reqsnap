"""Watch mode: poll a URL at intervals and snapshot changes."""

import time
import json
from typing import Callable, Optional

import requests

from reqsnap.logger import capture
from reqsnap.diff import diff_snapshots
from reqsnap.storage import save_snapshot


def _fetch_snapshot(url: str, method: str = "GET", headers: Optional[dict] = None,
                    environment: str = "default") -> dict:
    """Fetch a URL and return a captured snapshot dict."""
    headers = headers or {}
    response = requests.request(method, url, headers=headers, timeout=10)
    return capture(response, environment=environment)


def watch(
    url: str,
    interval: int = 30,
    method: str = "GET",
    headers: Optional[dict] = None,
    environment: str = "default",
    max_iterations: Optional[int] = None,
    on_change: Optional[Callable[[dict], None]] = None,
    save: bool = False,
) -> None:
    """Poll a URL at a given interval and report when the response changes.

    Args:
        url: The URL to watch.
        interval: Seconds between requests.
        method: HTTP method to use.
        headers: Optional request headers.
        environment: Environment label for snapshots.
        max_iterations: Stop after this many polls (None = run forever).
        on_change: Callback invoked with the diff dict when a change is detected.
        save: Whether to persist each snapshot to disk.
    """
    previous: Optional[dict] = None
    iteration = 0

    while max_iterations is None or iteration < max_iterations:
        current = _fetch_snapshot(url, method=method, headers=headers,
                                  environment=environment)
        if save:
            save_snapshot(current)

        if previous is not None:
            result = diff_snapshots(previous, current)
            if result["has_diff"] and on_change is not None:
                on_change(result)
        else:
            if on_change is not None:
                # Emit an initial "no previous" signal via a synthetic diff
                on_change({"has_diff": False, "initial": True, "snapshot": current})

        previous = current
        iteration += 1

        if max_iterations is None or iteration < max_iterations:
            time.sleep(interval)


def watch_to_json(diff_result: dict) -> str:
    """Serialize a diff result from watch to a JSON string."""
    return json.dumps(diff_result, indent=2)
