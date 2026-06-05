"""Clean inaccessible or unprocessed image files from DogeCloud OSS.

This script only deletes remote DogeCloud objects. It does not remove local image
files and does not delete image rows from the database.
"""

import argparse
import json
from dataclasses import dataclass
from typing import Any, Iterable

from contextlib import contextmanager

from db import database, models


@contextmanager
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@dataclass
class CleanupCandidate:
    """An image row whose remote object should be removed."""

    id: int
    image_path: str
    reason: str


def has_color_info(colors: Any) -> bool:
    """Return whether a JSON colors column contains usable color data."""
    if colors is None:
        return False

    if isinstance(colors, str):
        colors_text = colors.strip()
        if colors_text == "" or colors_text.lower() in {"null", "none"}:
            return False
        try:
            colors = json.loads(colors_text)
        except json.JSONDecodeError:
            return True

    if isinstance(colors, dict):
        if not colors:
            return False
        color_fields = ("primary_color", "color_primary", "colors", "color_series")
        for field in color_fields:
            value = colors.get(field)
            if value not in (None, "", [], {}):
                return True
        return any(value not in (None, "", [], {}) for value in colors.values())

    if isinstance(colors, (list, tuple, set)):
        return len(colors) > 0

    return bool(colors)


def get_cleanup_candidates(batch_size: int) -> Iterable[CleanupCandidate]:
    """Yield images that are inaccessible or missing color information."""
    with get_db() as db:
        query = (
            db.query(models.Image)
            .filter(models.Image.image_path.isnot(None))
            .yield_per(batch_size)
        )

        for image in query:
            reasons = []
            if image.accessable is False:
                reasons.append("accessable=false")
            if not has_color_info(image.colors):
                reasons.append("missing-colors")
            if not reasons:
                continue
            yield CleanupCandidate(
                id=image.id,
                image_path=image.image_path,
                reason=",".join(reasons),
            )


def mark_not_uploaded(image_id: int) -> None:
    """Mark an image as not uploaded after its remote object is removed."""
    with get_db() as db:
        db.query(models.Image).filter(models.Image.id == image_id).update(
            {"uploaded": False}, synchronize_session=False
        )
        db.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Delete DogeCloud OSS objects for database images that are "
            "inaccessible or have no color information. Local files are never deleted."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would be deleted without changing DogeCloud or the database.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of image rows to stream from the database at a time.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of remote files to process.",
    )
    parser.add_argument(
        "--keep-uploaded-flag",
        action="store_true",
        help="Do not set images.uploaded to false after deleting the remote file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    storage = None
    if not args.dry_run:
        from dogecloud import oss

        storage = oss.OSS()
    scanned = deleted = failed = 0

    for candidate in get_cleanup_candidates(args.batch_size):
        if args.limit is not None and scanned >= args.limit:
            break

        scanned += 1
        if args.dry_run:
            print(f"[DRY-RUN] {candidate.image_path} ({candidate.reason})")
            continue

        try:
            storage.delete_file(candidate.image_path)
            if not args.keep_uploaded_flag:
                mark_not_uploaded(candidate.id)
            deleted += 1
            print(f"[DELETED] {candidate.image_path} ({candidate.reason})")
        except Exception as exc:
            failed += 1
            print(f"[FAILED] {candidate.image_path} ({candidate.reason}): {exc}")

    if args.dry_run:
        print(f"Done. candidates={scanned}, deleted=0, failed=0")
    else:
        print(f"Done. candidates={scanned}, deleted={deleted}, failed={failed}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
