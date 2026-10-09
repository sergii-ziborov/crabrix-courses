#!/usr/bin/env python3
"""Attach the illustrated Atlas pattern panels to every other lesson.

Each unit contains ten patterns with three lessons each. Two shared images cover
five patterns apiece; alternating lessons therefore illustrate every pattern
while keeping the downloadable CoursePack reasonably small.
"""

import json
from pathlib import Path


COURSE = Path(__file__).resolve().parents[1] / "courses" / "algorithms"


def main() -> None:
    count = 0
    used_images: set[str] = set()
    for unit_path in sorted((COURSE / "units").glob("*.json")):
        unit = json.loads(unit_path.read_text(encoding="utf-8"))
        lesson_ids = unit["lessonIDs"]
        if len(lesson_ids) != 30:
            raise ValueError(f"Expected thirty lessons in {unit['id']}")
        for index, lesson_id in enumerate(lesson_ids):
            path = COURSE / "lessons" / f"{lesson_id}.json"
            lesson = json.loads(path.read_text(encoding="utf-8"))
            if index % 2:
                if "illustration" in lesson:
                    raise ValueError(f"Unexpected image in {lesson_id}")
                continue
            pattern_index = index // 3
            variant = "a" if pattern_index < 5 else "b"
            image_path = f"media/{unit['id']}-{variant}.png"
            if not (COURSE / image_path).is_file():
                raise FileNotFoundError(COURSE / image_path)
            panel = pattern_index % 5 + 1
            title = lesson["algorithm"]["patternID"].replace("-", " ").title()
            lesson["illustration"] = {
                "path": image_path,
                "alt": f"Five-panel {unit['title']} infographic; panel {panel} illustrates {title}.",
                "caption": f"{title}: follow panel {panel} to see the operation, then trace the lesson's own example.",
            }
            path.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            used_images.add(image_path)
            count += 1
    if count != 300 or len(used_images) != 40:
        raise ValueError(f"Expected 300 lessons and 40 images, got {count} and {len(used_images)}")
    print(f"Attached {len(used_images)} infographics to {count} Atlas lessons")


if __name__ == "__main__":
    main()
