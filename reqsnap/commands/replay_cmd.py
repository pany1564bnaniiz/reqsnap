"""CLI command handler for the 'replay' subcommand."""

import sys
import json

from reqsnap.replay import replay_snapshot
from reqsnap.diff import diff_snapshots
from reqsnap.report import format_diff_report
from reqsnap.storage import save_snapshot, list_snapshots


def handle_replay(args) -> int:
    """Replay a snapshot and optionally diff against the original.

    Returns exit code: 0 for success, 1 for errors or detected diffs.
    """
    snapshot_id = args.snapshot_id
    environment = getattr(args, "environment", "replayed")
    override_url = getattr(args, "url", None)
    save = getattr(args, "save", False)
    compare = getattr(args, "compare", False)
    output_format = getattr(args, "format", "text")

    try:
        replayed = replay_snapshot(
            snapshot_id,
            environment=environment,
            override_url=override_url,
        )
    except FileNotFoundError:
        print(f"[reqsnap] Snapshot '{snapshot_id}' not found.", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"[reqsnap] Replay failed: {exc}", file=sys.stderr)
        return 1

    if save:
        path = save_snapshot(replayed)
        print(f"[reqsnap] Replayed snapshot saved: {path}")

    if compare:
        from reqsnap.storage import load_snapshot as _load
        original = _load(snapshot_id)
        diff = diff_snapshots(original, replayed)

        if output_format == "json":
            print(json.dumps(diff, indent=2))
        else:
            print(format_diff_report(diff))

        return 1 if diff.get("has_diff") else 0

    if output_format == "json":
        print(json.dumps(replayed, indent=2))
    else:
        status = replayed.get("response_status")
        url = replayed.get("url")
        elapsed = replayed.get("elapsed_ms")
        print(f"[reqsnap] Replayed {url} -> HTTP {status} ({elapsed}ms) [{environment}]")

    return 0


def register_parser(subparsers) -> None:
    """Register the 'replay' subcommand with the given subparsers object."""
    parser = subparsers.add_parser(
        "replay",
        help="Replay a captured snapshot against a target environment",
    )
    parser.add_argument("snapshot_id", help="ID of the snapshot to replay")
    parser.add_argument("--url", default=None, help="Override the request URL")
    parser.add_argument("--environment", default="replayed", help="Label for the replayed environment")
    parser.add_argument("--save", action="store_true", help="Save the replayed snapshot to disk")
    parser.add_argument("--compare", action="store_true", help="Diff the replay against the original")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.set_defaults(func=handle_replay)
