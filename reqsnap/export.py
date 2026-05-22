"""Export snapshots and diff results to various formats (JSON, HTML, Markdown)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


SUPPORTED_FORMATS = ("json", "html", "markdown")


def _render_html(diff: Dict[str, Any]) -> str:
    """Render a diff result as a minimal HTML report."""
    env_a = diff.get("environment_a", "env_a")
    env_b = diff.get("environment_b", "env_b")
    has_diff = diff.get("has_diff", False)
    status_color = "#c0392b" if has_diff else "#27ae60"
    status_text = "Differences Found" if has_diff else "Identical"

    rows = ""
    for change in diff.get("changes", []):
        key = change.get("key", "")
        old_val = change.get("value_a", "")
        new_val = change.get("value_b", "")
        rows += (
            f"<tr><td>{key}</td>"
            f"<td style='color:#c0392b'>{old_val}</td>"
            f"<td style='color:#27ae60'>{new_val}</td></tr>\n"
        )

    return f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'><title>reqsnap diff report</title></head>
<body>
<h1>reqsnap Diff Report</h1>
<p>Generated: {datetime.utcnow().isoformat()}Z</p>
<p>Environments: <strong>{env_a}</strong> vs <strong>{env_b}</strong></p>
<p>Status: <span style='color:{status_color}'>{status_text}</span></p>
<table border='1' cellpadding='6' cellspacing='0'>
<thead><tr><th>Key</th><th>{env_a}</th><th>{env_b}</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</body></html>
"""


def _render_markdown(diff: Dict[str, Any]) -> str:
    """Render a diff result as a Markdown report."""
    env_a = diff.get("environment_a", "env_a")
    env_b = diff.get("environment_b", "env_b")
    has_diff = diff.get("has_diff", False)
    status_text = "❌ Differences Found" if has_diff else "✅ Identical"

    lines = [
        "# reqsnap Diff Report",
        f"> Generated: {datetime.utcnow().isoformat()}Z",
        "",
        f"**Environments:** `{env_a}` vs `{env_b}`",
        f"**Status:** {status_text}",
        "",
    ]

    changes = diff.get("changes", [])
    if changes:
        lines += [f"| Key | {env_a} | {env_b} |", "|-----|---------|---------|"]
        for change in changes:
            key = change.get("key", "")
            old_val = change.get("value_a", "")
            new_val = change.get("value_b", "")
            lines.append(f"| `{key}` | `{old_val}` | `{new_val}` |")
    else:
        lines.append("_No differences detected._")

    return "\n".join(lines) + "\n"


def export_diff(
    diff: Dict[str, Any],
    fmt: str = "json",
    output_path: Optional[Path] = None,
) -> str:
    """Export a diff result to the specified format.

    Args:
        diff: The diff dict produced by diff_snapshots.
        fmt: One of 'json', 'html', 'markdown'.
        output_path: If provided, write the result to this file.

    Returns:
        The rendered string content.

    Raises:
        ValueError: If an unsupported format is requested.
    """
    fmt = fmt.lower()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    if fmt == "json":
        content = json.dumps(diff, indent=2)
    elif fmt == "html":
        content = _render_html(diff)
    else:  # markdown
        content = _render_markdown(diff)

    if output_path is not None:
        Path(output_path).write_text(content, encoding="utf-8")

    return content
