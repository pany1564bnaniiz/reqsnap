"""CLI command handler for searching snapshots."""

import json
import argparse
from pathlib import Path

from reqsnap.search import search_snapshots
from reqsnap.storage import _snapshot_dir


def handle_search(args: argparse.Namespace) -> None:
    """Execute the search command and print matching snapshots."""
    snapshot_dir = _snapshot_dir()

    if not snapshot_dir.exists():
        print("No snapshots directory found. Capture some requests first.")
        return

    snapshot_files = list(snapshot_dir.glob("*.json"))
    if not snapshot_files:
        print("No snapshots found.")
        return

    results = search_snapshots(
        snapshot_files=snapshot_files,
        query=args.query,
        field=args.field,
        case_sensitive=args.case_sensitive,
    )

    if not results:
        print(f"No snapshots matched query: '{args.query}'")
        return

    print(f"Found {len(results)} matching snapshot(s):\n")
    for snap in results:
        url = snap.get("url", "unknown")
        method = snap.get("method", "UNKNOWN")
        env = snap.get("environment", "default")
        status = snap.get("response", {}).get("status_code", "?")
        name = snap.get("_source_file", "")
        print(f"  [{method}] {url}  status={status}  env={env}  file={name}")

    if args.json:
        # Strip internal metadata before printing
        clean = [{k: v for k, v in s.items() if k != "_source_file"} for s in results]
        print("\nJSON output:")
        print(json.dumps(clean, indent=2))


def register_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'search' subcommand with the argument parser."""
    parser = subparsers.add_parser(
        "search",
        help="Search through captured snapshots by field value.",
    )
    parser.add_argument(
        "query",
        help="The search term to look for.",
    )
    parser.add_argument(
        "--field",
        default=None,
        help="Restrict search to a specific top-level field (e.g. url, method, environment).",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        default=False,
        help="Perform a case-sensitive search (default: case-insensitive).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Also print matching snapshots as JSON.",
    )
    parser.set_defaults(func=handle_search)
