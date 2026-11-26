from __future__ import annotations

import argparse
import sys

from . import storage
from .models import Snapshot

def format_snapshot(s: Snapshot) -> str:
    lines = [
        f"#{s.id}  {s.task}",
        f"  saved:  {s.created_at.astimezone():%Y-%m-%d %H:%M} on {s.device}",
    ]
    if s.next_step:
        lines.append(f"  next:   {s.next_step}")
    if s.notes:
        lines.append(f"  notes:  {s.notes}")
    for link in s.links:
        lines.append(f"  link:   {link}")
    if s.tags:
        lines.append(f"  tags:   {', '.join(s.tags)}")
    return "\n".join(lines)
def cmd_save(args: argparse.Namespace, conn) -> int:
    snap = Snapshot(
        task=args.task,
        next_step=args.next,
        notes=args.notes,
        links=args.link or [],
        tags=args.tag or [],
    )
    storage.save(conn, snap)
    print(f"Saved snapshot #{snap.id}.")
    return 0
def cmd_resume(args: argparse.Namespace, conn) -> int:
    snap = storage.latest(conn)
    if snap is None:
        print('No snapshots yet. Save one with: switchlog save "what you are doing"')
        return 1
    print(format_snapshot(snap))
    return 0
def cmd_list(args: argparse.Namespace, conn) -> int:
    snaps = storage.list_snapshots(conn, limit=args.limit, tag=args.tag)
    if not snaps:
        print("No snapshots found.")
        return 0
    for s in snaps:
        tags = f"  [{', '.join(s.tags)}]" if s.tags else ""
        print(f"#{s.id:<4} {s.created_at.astimezone():%Y-%m-%d %H:%M}  {s.task}{tags}")
    return 0
def cmd_show(args: argparse.Namespace, conn) -> int:
    snap = storage.get(conn, args.id)
    if snap is None:
        print(f"No snapshot with ID {args.id}. Run 'switchlog list' to see IDs.", file=sys.stderr)
        return 1
    print(format_snapshot(snap))
    return 0
def cmd_delete(args: argparse.Namespace, conn) -> int:
    if storage.delete(conn, args.id):
        print(f"Deleted snapshot #{args.id}.")
        return 0
    print(f"No snapshot with ID {args.id}.", file=sys.stderr)
    return 1

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="switchlog", description="Save and resume context snapshots."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("save", help="Save a context snapshot.")
    p.add_argument("task", help="What you are working on.")
    p.add_argument("--next", help="The next step when you come back.")
    p.add_argument("--notes", help="Free-form notes.")
    p.add_argument("--link", action="append", help="A related URL (repeatable).")
    p.add_argument("--tag", action="append", help="A tag (repeatable).")
    p.set_defaults(func=cmd_save)
    p = sub.add_parser("resume", help="Show the latest snapshot.")
    p.set_defaults(func=cmd_resume)
    p = sub.add_parser("list", help="List snapshots, newest first.")
    p.add_argument("--limit", type=int, help="Show at most N snapshots.")
    p.add_argument("--tag", help="Only show snapshots with this tag.")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="Show one snapshot in full.")
    p.add_argument("id", type=int, help="Snapshot ID (see 'switchlog list').")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("delete", help="Delete a snapshot.")
    p.add_argument("id", type=int, help="Snapshot ID.")
    p.set_defaults(func=cmd_delete)
    return parser
def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    conn = storage.connect()
    try:
        return args.func(args, conn)
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())