"""CLI: scan batch inbox folder and queue videos for processing."""

from __future__ import annotations

import argparse
import asyncio
import sys

from app.config import get_settings
from app.database import async_session, init_db
from app.services.batch_folder import ensure_inbox_dirs, ingest_inbox_folder, inbox_status, resolve_inbox


async def run_scan(folder: str | None, league: str | None, max_files: int | None) -> int:
    await init_db()
    settings = get_settings()
    inbox = resolve_inbox(folder, settings)
    ensure_inbox_dirs(inbox)

    async with async_session() as session:
        result = await ingest_inbox_folder(
            session,
            folder=folder,
            league=league,
            max_files=max_files,
        )

    print(f"Inbox: {result.inbox_path}")
    print(f"Scanned: {result.scanned} | Queued: {result.queued} | Failed: {result.failed}")
    for job in result.jobs:
        print(f"  ✓ {job.title} → job {job.id}")
    for err in result.errors:
        print(f"  ✗ {err}", file=sys.stderr)
    return 0 if result.failed == 0 else 1


async def run_watch(
    folder: str | None,
    league: str | None,
    max_files: int | None,
    interval: int,
) -> None:
    await init_db()
    settings = get_settings()
    inbox = resolve_inbox(folder, settings)
    ensure_inbox_dirs(inbox)
    print(f"Watching {inbox} every {interval}s (Ctrl+C to stop)")
    while True:
        async with async_session() as session:
            result = await ingest_inbox_folder(
                session,
                folder=folder,
                league=league,
                max_files=max_files,
            )
        if result.queued:
            print(f"Queued {result.queued} video(s)")
        await asyncio.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan a folder of cricket videos and queue them for short generation.",
    )
    parser.add_argument(
        "--folder",
        help="Inbox folder path (default: storage/inbox from config)",
    )
    parser.add_argument("--league", choices=["ipl", "icc", "generic"], default="ipl")
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Keep watching the folder for new videos",
    )
    parser.add_argument("--interval", type=int, default=10, help="Watch interval in seconds")
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print inbox status and exit",
    )
    args = parser.parse_args()

    if args.status:
        info = inbox_status(args.folder)
        for key, value in info.items():
            print(f"{key}: {value}")
        return

    if args.watch:
        asyncio.run(run_watch(args.folder, args.league, args.max_files, args.interval))
    else:
        code = asyncio.run(run_scan(args.folder, args.league, args.max_files))
        sys.exit(code)


if __name__ == "__main__":
    main()
