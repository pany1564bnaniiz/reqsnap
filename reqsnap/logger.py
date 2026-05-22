"""HTTP request/response logger for reqsnap."""

import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class RequestSnapshot:
    """Represents a captured HTTP request and its response."""

    url: str
    method: str
    status_code: int
    response_body: Any
    request_headers: Dict[str, str] = field(default_factory=dict)
    response_headers: Dict[str, str] = field(default_factory=dict)
    request_body: Optional[Any] = None
    elapsed_ms: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    environment: str = "default"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


def capture(url: str, method: str = "GET", environment: str = "default", **kwargs) -> RequestSnapshot:
    """Perform an HTTP request and capture it as a snapshot.

    Args:
        url: Target URL.
        method: HTTP method (GET, POST, etc.).
        environment: Label for the environment (e.g. 'staging', 'prod').
        **kwargs: Additional arguments forwarded to requests.request().

    Returns:
        A RequestSnapshot instance with the captured data.
    """
    import requests  # local import to keep the module lightweight

    start = time.perf_counter()
    response = requests.request(method, url, **kwargs)
    elapsed_ms = (time.perf_counter() - start) * 1000

    try:
        response_body = response.json()
    except ValueError:
        response_body = response.text

    request_body = kwargs.get("json") or kwargs.get("data")

    return RequestSnapshot(
        url=url,
        method=method.upper(),
        status_code=response.status_code,
        response_body=response_body,
        request_headers=dict(response.request.headers),
        response_headers=dict(response.headers),
        request_body=request_body,
        elapsed_ms=round(elapsed_ms, 2),
        environment=environment,
    )
