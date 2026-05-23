"""CLI command handler for pinning and unpinning snapshots."""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from reqsnap.pin import pin_snapshot, unpin_snapshot, is_pinned, filter_pinned, list_pinned_ids


def _load_and_update(path: Path, fn) -> None:
    """Load a snapshot file, apply fn, and write it back."""
    data = json.loads(path.read_text(encoding="utf-8"))
    updated = fn(data)
    path.write_text(json.dumps(updated, indent=2), encoding="utf-8")


def handle_pin(args: Namespace) -> None:
    snap_path = Path(args.snapshot)
    if not snap_path.exists():
        print(f"[reqsnap] Snapshot not found: {snap_path}", file=sys.stderr)
        sys.exit(1)

    if args.action == "pin":
        _load_and_update(snap_path, pin_snapshot)
        print(f"[reqsnap] Pinned: {snap_path.name}")
    elif args.action == "unpin":
        _load_and_update(snap_path, unpin_snapshot)
        print(f"[reqsnap] Unpinned: {snap_path.name}")
    elif args.action == "list":
        directory = Path(args.snapshot)
        if not directory.is_dir():
            print("[reqsnap] Provide a directory path for 'list' action.", file=sys.stderr)
            sys.exit(1)
        snapshots = []
        for f in sorted(directory.glob("*.json")):
            try:
                snapshots.append(json.loads(f.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue
        pinned = filter_pinned(snapshots)
        if not pinned:
            print("[reqsnap] No pinned snapshots found.")
        else:
            ids = list_pinned_ids(pinned)
            print(f"[reqsnap] Pinned snapshots ({len(ids)}):")
            for ident in ids:
                print(f"  - {ident}")
    elif args.action == "status":
        data = json.loads(snap_path.read_text(encoding="utf-8"))
        status = "pinned" if is_pinned(data) else "unpinned"
        print(f"[reqsnap] {snap_path.name}: {status}")


def register_parser(subparsers) -> None:
    parser: ArgumentParser = subparsers.add_parser(
        "pin", help="Pin or unpin snapshots as reference baselines"
    )
    parser.add_argument(
        "action",
        choices=["pin", "unpin", "status", "list"],
        help="Action to perform",
    )
    parser.add_argument(
        "snapshot",
        help="Path to snapshot file (or directory for 'list')",
    )
    parser.set_defaults(func=handle_pin)
