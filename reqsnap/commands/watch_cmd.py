"""CLI command handler for the watch subcommand."""

import argparse
import sys

from reqsnap.watch import watch, watch_to_json
from reqsnap.report import format_diff_report


def _on_change_handler(diff: dict, output_format: str) -> None:
    """Print change notification based on the requested output format."""
    if diff.get("initial"):
        print("[reqsnap] Watching started — initial snapshot captured.")
        return

    if output_format == "json":
        print(watch_to_json(diff))
    else:
        print("\n[reqsnap] Change detected!")
        print(format_diff_report(diff))


def handle_watch(args: argparse.Namespace) -> int:
    """Entry point for the watch subcommand.

    Returns:
        Exit code (0 on success, 1 on error).
    """
    headers: dict = {}
    if args.header:
        for h in args.header:
            if ":" not in h:
                print(f"[reqsnap] Invalid header format (expected Key:Value): {h}",
                      file=sys.stderr)
                return 1
            key, _, value = h.partition(":")
            headers[key.strip()] = value.strip()

    output_format = getattr(args, "format", "text")

    try:
        watch(
            url=args.url,
            interval=args.interval,
            method=args.method.upper(),
            headers=headers,
            environment=args.environment,
            max_iterations=args.iterations,
            on_change=lambda diff: _on_change_handler(diff, output_format),
            save=args.save,
        )
    except KeyboardInterrupt:
        print("\n[reqsnap] Watch stopped.")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[reqsnap] Error during watch: {exc}", file=sys.stderr)
        return 1

    return 0


def register_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the watch subcommand with the given subparsers."""
    parser = subparsers.add_parser("watch", help="Poll a URL and report changes")
    parser.add_argument("url", help="URL to watch")
    parser.add_argument("--interval", type=int, default=30,
                        help="Seconds between requests (default: 30)")
    parser.add_argument("--method", default="GET", help="HTTP method (default: GET)")
    parser.add_argument("--header", action="append", metavar="Key:Value",
                        help="Request header (repeatable)")
    parser.add_argument("--environment", default="default",
                        help="Environment label for snapshots")
    parser.add_argument("--iterations", type=int, default=None,
                        help="Stop after N polls (default: run forever)")
    parser.add_argument("--save", action="store_true",
                        help="Persist each snapshot to disk")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.set_defaults(func=handle_watch)
