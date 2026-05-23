"""CLI command for managing snapshot tags."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from reqsnap import storage, tag


def handle_tag(args: argparse.Namespace) -> None:
    """Dispatch tag sub-commands: add, remove, list."""
    snap_dir = Path(args.directory) if getattr(args, "directory", None) else storage._snapshot_dir()

    if args.tag_action == "list":
        snapshots = [
            json.loads(p.read_text())
            for p in snap_dir.glob("*.json")
            if p.is_file()
        ]
        tags = tag.list_tags(snapshots)
        if not tags:
            print("No tags found.")
        else:
            for t in tags:
                print(t)
        return

    # add / remove require a snapshot id and a tag name
    snap_path = snap_dir / f"{args.snapshot_id}.json"
    if not snap_path.exists():
        print(f"Snapshot '{args.snapshot_id}' not found.", file=sys.stderr)
        sys.exit(1)

    snapshot = json.loads(snap_path.read_text())

    if args.tag_action == "add":
        updated = tag.add_tag(snapshot, args.tag_name)
        print(f"Added tag '{args.tag_name}' to {args.snapshot_id}.")
    elif args.tag_action == "remove":
        updated = tag.remove_tag(snapshot, args.tag_name)
        print(f"Removed tag '{args.tag_name}' from {args.snapshot_id}.")
    else:
        print(f"Unknown tag action: {args.tag_action}", file=sys.stderr)
        sys.exit(1)

    snap_path.write_text(json.dumps(updated, indent=2))


def register_parser(subparsers) -> None:
    """Register the 'tag' command with the CLI argument parser."""
    parser = subparsers.add_parser("tag", help="Manage snapshot tags")
    parser.add_argument(
        "--directory", "-d", default=None, help="Snapshot storage directory"
    )

    tag_sub = parser.add_subparsers(dest="tag_action", required=True)

    add_p = tag_sub.add_parser("add", help="Add a tag to a snapshot")
    add_p.add_argument("snapshot_id", help="Snapshot filename without .json")
    add_p.add_argument("tag_name", help="Tag to add")

    rem_p = tag_sub.add_parser("remove", help="Remove a tag from a snapshot")
    rem_p.add_argument("snapshot_id", help="Snapshot filename without .json")
    rem_p.add_argument("tag_name", help="Tag to remove")

    tag_sub.add_parser("list", help="List all tags across stored snapshots")

    parser.set_defaults(func=handle_tag)
