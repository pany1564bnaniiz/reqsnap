"""CLI command for comparing multiple saved snapshots."""

import argparse
import json
import sys
from pathlib import Path

from reqsnap.storage import load_snapshot
from reqsnap.compare import compare_snapshots, summarize_comparison


def handle_compare(args: argparse.Namespace) -> None:
    """Load snapshots by name and print a comparison report."""
    if len(args.snapshots) < 2:
        print("Error: provide at least two snapshot names.", file=sys.stderr)
        sys.exit(1)

    loaded = []
    for name in args.snapshots:
        try:
            snap = load_snapshot(name, directory=args.directory)
            loaded.append(snap)
        except FileNotFoundError:
            print(f"Error: snapshot '{name}' not found.", file=sys.stderr)
            sys.exit(1)

    ignore = args.ignore.split(",") if args.ignore else None

    try:
        report = compare_snapshots(loaded, ignore_keys=ignore, only_diffs=args.only_diffs)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(summarize_comparison(report))


def register_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'compare' subcommand."""
    parser = subparsers.add_parser(
        "compare",
        help="Compare two or more saved snapshots",
    )
    parser.add_argument(
        "snapshots",
        nargs="+",
        metavar="SNAPSHOT",
        help="Names of snapshots to compare (at least two)",
    )
    parser.add_argument(
        "--directory",
        default=None,
        help="Directory where snapshots are stored",
    )
    parser.add_argument(
        "--ignore",
        default=None,
        metavar="KEYS",
        help="Comma-separated body keys to ignore during comparison",
    )
    parser.add_argument(
        "--only-diffs",
        action="store_true",
        help="Only show pairs that have differences",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    parser.set_defaults(func=handle_compare)
