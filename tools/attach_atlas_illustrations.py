#!/usr/bin/env python3
"""Attach the illustrated Atlas pattern panels to every lesson.

Each unit contains ten patterns with three lessons each. Two shared images cover
five patterns apiece, so all three steps can use the same relevant panel without
duplicating image bytes in the downloadable CoursePack.
"""

import json
from pathlib import Path


COURSE = Path(__file__).resolve().parents[1] / "courses" / "algorithms"


def main() -> None:
    count = 0
    covered = 0
    used_images: set[str] = set()
    for unit_path in sorted((COURSE / "units").glob("*.json")):
        unit = json.loads(unit_path.read_text(encoding="utf-8"))
        lesson_ids = unit["lessonIDs"]
        if len(lesson_ids) != 30:
            raise ValueError(f"Expected thirty lessons in {unit['id']}")
        for index, lesson_id in enumerate(lesson_ids):
            path = COURSE / "lessons" / f"{lesson_id}.json"
            lesson = json.loads(path.read_text(encoding="utf-8"))
            pattern_index = index // 3
            variant = "a" if pattern_index < 5 else "b"
            image_path = f"media/{unit['id']}-{variant}.png"
            if not (COURSE / image_path).is_file():
                raise FileNotFoundError(COURSE / image_path)
            panel = pattern_index % 5 + 1
            title = lesson["algorithm"]["patternID"].replace("-", " ").title()
            illustration = {
                "path": image_path,
                "alt": f"Five-panel {unit['title']} infographic; panel {panel} illustrates {title}.",
                "caption": f"{title}: follow panel {panel} to see the operation, then trace this lesson's example.",
            }
            if "illustration" not in lesson:
                lesson["illustration"] = illustration
                path.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                count += 1
            elif lesson["illustration"]["path"] != image_path:
                raise ValueError(f"Wrong pattern panel in {lesson_id}")
            used_images.add(image_path)
            covered += 1
    if covered != 600 or len(used_images) != 40:
        raise ValueError(f"Expected 600 lessons and 40 images, got {covered} and {len(used_images)}")
    print(f"Covered {covered} Atlas lessons with {len(used_images)} images; added {count} links")


if __name__ == "__main__":
    main()
