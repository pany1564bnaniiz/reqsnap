"""Generate human-readable diff reports from snapshot comparisons."""

from typing import Optional


_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{_RESET}"


def format_diff_report(diff: dict, use_color: bool = True) -> str:
    """Render a diff dict (from ``diff_snapshots``) as a readable string.

    Args:
        diff: The diff dictionary produced by ``diff_snapshots``.
        use_color: Whether to include ANSI colour codes.

    Returns:
        Multi-line string report.
    """
    lines = []
    env_a = diff.get("environment_a", "env_a")
    env_b = diff.get("environment_b", "env_b")
    has_diff = diff.get("has_diff", False)

    header = _colorize(
        f"=== reqsnap diff: {env_a} vs {env_b} ===",
        _BOLD,
        use_color,
    )
    lines.append(header)

    status_line = (
        _colorize("DIFFERENCES FOUND", _RED, use_color)
        if has_diff
        else _colorize("IDENTICAL", _GREEN, use_color)
    )
    lines.append(f"Status : {status_line}")
    lines.append(f"URL    : {diff.get('url', 'N/A')}")
    lines.append(f"Method : {diff.get('method', 'N/A')}")
    lines.append("")

    status_diff = diff.get("status_code")
    if status_diff and status_diff.get("differs"):
        lines.append(_colorize("[Status Code]  CHANGED", _YELLOW, use_color))
        lines.append(f"  {env_a}: {status_diff['a']}")
        lines.append(f"  {env_b}: {status_diff['b']}")
        lines.append("")

    body_diff = diff.get("body", {})
    if body_diff.get("differs"):
        lines.append(_colorize("[Body]  CHANGED", _YELLOW, use_color))
        for change in body_diff.get("changes", []):
            key = change.get("key", "?")
            val_a = change.get("a", "<missing>")
            val_b = change.get("b", "<missing>")
            lines.append(f"  .{key}")
            lines.append(_colorize(f"    - {val_a}", _RED, use_color))
            lines.append(_colorize(f"    + {val_b}", _GREEN, use_color))
        lines.append("")

    headers_diff = diff.get("headers", {})
    if headers_diff.get("differs"):
        lines.append(_colorize("[Headers]  CHANGED", _YELLOW, use_color))
        for change in headers_diff.get("changes", []):
            key = change.get("key", "?")
            val_a = change.get("a", "<missing>")
            val_b = change.get("b", "<missing>")
            lines.append(f"  {key}")
            lines.append(_colorize(f"    - {val_a}", _RED, use_color))
            lines.append(_colorize(f"    + {val_b}", _GREEN, use_color))
        lines.append("")

    lines.append("=" * 40)
    return "\n".join(lines)
