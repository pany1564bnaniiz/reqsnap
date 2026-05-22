"""CLI entry point for reqsnap — compare two snapshot JSON files."""

import argparse
import json
import sys
from pathlib import Path

from reqsnap.diff import diff_snapshots, diff_to_json


def load_snapshot(path: str) -> dict:
    """Load a snapshot from a JSON file."""
    file_path = Path(path)
    if not file_path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with file_path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid JSON in {path}: {exc}", file=sys.stderr)
            sys.exit(1)


def print_diff_summary(report: dict) -> None:
    """Print a human-readable summary of the diff report."""
    env_a = report["environment_a"]
    env_b = report["environment_b"]
    print(f"Comparing snapshots: [{env_a}] vs [{env_b}]")
    print(f"Has differences: {report['has_diff']}")
    print()

    for entry in report["diffs"]:
        status = entry["status"]
        key = entry["key"]
        if status == "unchanged":
            continue
        left = entry.get("left")
        right = entry.get("right")
        marker = {"added": "+", "removed": "-", "changed": "~"}.get(status, "?")
        print(f"  [{marker}] {key}: {left!r} -> {right!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reqsnap",
        description="Compare two reqsnap JSON snapshot files.",
    )
    parser.add_argument("snapshot_a", help="Path to the first snapshot JSON file.")
    parser.add_argument("snapshot_b", help="Path to the second snapshot JSON file.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the diff report as JSON instead of human-readable text.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    snap_a = load_snapshot(args.snapshot_a)
    snap_b = load_snapshot(args.snapshot_b)

    report = diff_snapshots(snap_a, snap_b)

    if args.json:
        print(diff_to_json(report))
    else:
        print_diff_summary(report)

    return 1 if report["has_diff"] else 0


if __name__ == "__main__":
    sys.exit(main())
