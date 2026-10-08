#!/usr/bin/env python3
"""Refresh nested CoursePack content digests after authored lesson edits."""

import argparse
import hashlib
import json
from pathlib import Path

from coursepack import read_course


def digest(value: dict) -> str:
    payload = {key: item for key, item in value.items() if key != "contentDigest"}
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).replace("/", "\\/").encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def update(path: Path, combined: dict) -> None:
    authored = json.loads(path.read_text(encoding="utf-8"))
    current = digest(combined)
    if authored.get("contentDigest") != current:
        authored["contentDigest"] = current
        path.write_text(json.dumps(authored, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course", nargs="+", help="Course IDs to refresh")
    parser.add_argument("--courses", type=Path, default=Path("courses"))
    args = parser.parse_args()
    for course_id in args.course:
        root = args.courses / course_id
        if not (root / "course.json").is_file():
            parser.error(f"unknown course: {course_id}")
        course = read_course(root)
        for unit in course["units"]:
            for lesson in unit["lessons"]:
                update(root / "lessons" / f"{lesson['id']}.json", lesson)
        course = read_course(root)
        for unit in course["units"]:
            update(root / "units" / f"{unit['id']}.json", unit)
        update(root / "course.json", read_course(root))
        print(f"Updated {course_id}")


if __name__ == "__main__":
    main()
