"""Snapshot schema validation utilities for reqsnap."""

from typing import Any, Dict, List, Optional

REQUIRED_KEYS = {"url", "method", "status_code", "headers", "body", "timestamp", "environment"}

VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE"}


def _check_required_keys(snapshot: Dict[str, Any]) -> List[str]:
    """Return list of missing required keys."""
    return [key for key in REQUIRED_KEYS if key not in snapshot]


def _check_status_code(snapshot: Dict[str, Any]) -> Optional[str]:
    """Return error string if status_code is invalid, else None."""
    code = snapshot.get("status_code")
    if not isinstance(code, int):
        return f"status_code must be an integer, got {type(code).__name__}"
    if not (100 <= code <= 599):
        return f"status_code {code} is out of valid HTTP range (100-599)"
    return None


def _check_method(snapshot: Dict[str, Any]) -> Optional[str]:
    """Return error string if method is invalid, else None."""
    method = snapshot.get("method", "")
    if not isinstance(method, str):
        return f"method must be a string, got {type(method).__name__}"
    if method.upper() not in VALID_METHODS:
        return f"method '{method}' is not a recognised HTTP method"
    return None


def _check_headers(snapshot: Dict[str, Any]) -> Optional[str]:
    """Return error string if headers field is invalid, else None."""
    headers = snapshot.get("headers")
    if not isinstance(headers, dict):
        return f"headers must be a dict, got {type(headers).__name__}"
    return None


def validate_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a snapshot dict.

    Returns a result dict with keys:
      - valid (bool)
      - errors (list of str)
    """
    errors: List[str] = []

    missing = _check_required_keys(snapshot)
    if missing:
        errors.append(f"Missing required keys: {', '.join(sorted(missing))}")
        return {"valid": False, "errors": errors}

    for checker in (_check_status_code, _check_method, _check_headers):
        err = checker(snapshot)
        if err:
            errors.append(err)

    return {"valid": len(errors) == 0, "errors": errors}


def validate_all(snapshots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate a list of snapshots.

    Returns a list of result dicts, each with an added 'index' key.
    """
    results = []
    for i, snap in enumerate(snapshots):
        result = validate_snapshot(snap)
        result["index"] = i
        results.append(result)
    return results
