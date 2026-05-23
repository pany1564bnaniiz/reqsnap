"""CLI command: group snapshots by a field and print a summary table."""

import argparse
import json
from pathlib import Path

from reqsnap.group import SUPPORTED_FIELDS, group_by, group_summary, largest_group
from reqsnap.storage import list_snapshots, load_snapshot


def handle_group(args: argparse.Namespace) -> None:
    snap_dir = Path(args.directory) if args.directory else Path("snapshots")

    if not snap_dir.exists():
        print(f"[warn] Snapshot directory not found: {snap_dir}")
        return

    paths = list_snapshots(snap_dir)
    if not paths:
        print("No snapshots found.")
        return

    snapshots = []
    for p in paths:
        try:
            snapshots.append(load_snapshot(p))
        except Exception:
            continue

    try:
        groups = group_by(snapshots, args.field)
    except ValueError as exc:
        print(f"[error] {exc}")
        return

    summary = group_summary(groups)
    biggest = largest_group(groups)

    if args.json:
        print(json.dumps({"field": args.field, "groups": summary}, indent=2))
        return

    print(f"Grouped {len(snapshots)} snapshot(s) by '{args.field}'\n")
    print(f"  {'Key':<30} {'Count':>6}")
    print("  " + "-" * 38)
    for entry in summary:
        marker = " *" if entry["key"] == biggest else ""
        print(f"  {entry['key']:<30} {entry['count']:>6}{marker}")
    print()
    print(f"  * largest group")


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("group", help="Group snapshots by a field")
    p.add_argument(
        "field",
        choices=SUPPORTED_FIELDS,
        help="Field to group snapshots on",
    )
    p.add_argument("--directory", "-d", help="Snapshot directory (default: snapshots)")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.set_defaults(func=handle_group)
