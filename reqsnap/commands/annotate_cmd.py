"""CLI command handler for snapshot annotations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from reqsnap.annotate import add_annotation, list_annotations, remove_annotation


def handle_annotate(args: argparse.Namespace) -> None:
    path = Path(args.snapshot)
    if not path.exists():
        print(f"[reqsnap] Snapshot not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[reqsnap] Invalid JSON in snapshot: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.annotate_action == "add":
        updated = add_annotation(snapshot, args.note, author=args.author)
        path.write_text(json.dumps(updated, indent=2), encoding="utf-8")
        idx = len(updated["annotations"]) - 1
        print(f"[reqsnap] Annotation #{idx} added to {path.name}")

    elif args.annotate_action == "remove":
        try:
            updated = remove_annotation(snapshot, args.index)
        except IndexError as exc:
            print(f"[reqsnap] {exc}", file=sys.stderr)
            sys.exit(1)
        path.write_text(json.dumps(updated, indent=2), encoding="utf-8")
        print(f"[reqsnap] Annotation #{args.index} removed from {path.name}")

    elif args.annotate_action == "list":
        annotations = list_annotations(snapshot)
        if not annotations:
            print("(no annotations)")
        for i, ann in enumerate(annotations):
            print(f"  [{i}] {ann['timestamp']} ({ann['author']}): {ann['note']}")


def register_parser(subparsers) -> None:
    parser = subparsers.add_parser("annotate", help="Manage snapshot annotations")
    sub = parser.add_subparsers(dest="annotate_action", required=True)

    add_p = sub.add_parser("add", help="Add an annotation to a snapshot")
    add_p.add_argument("snapshot", help="Path to snapshot JSON file")
    add_p.add_argument("note", help="Annotation text")
    add_p.add_argument("--author", default="reqsnap", help="Author name (default: reqsnap)")

    rm_p = sub.add_parser("remove", help="Remove an annotation by index")
    rm_p.add_argument("snapshot", help="Path to snapshot JSON file")
    rm_p.add_argument("index", type=int, help="Zero-based index of the annotation to remove")

    ls_p = sub.add_parser("list", help="List annotations on a snapshot")
    ls_p.add_argument("snapshot", help="Path to snapshot JSON file")

    parser.set_defaults(func=handle_annotate)
