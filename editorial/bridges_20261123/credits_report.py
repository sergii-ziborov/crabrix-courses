#!/usr/bin/env python3
"""Write CREDITS.md for a bridge course: each credited Academy lesson, its rule,
and the bridge lesson's own rule and check that stand in for it."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
course_id = sys.argv[1]
course_dir = ROOT / "courses" / course_id
course = json.loads((course_dir / "course.json").read_text())
lines = [f"# Credits — {course['title']}", "",
         "Finishing a bridge lesson marks these Academy lessons as known in the app.",
         "Each row names the target lesson's rule and the bridge lesson rule and check that cover it.", ""]
for unit_id in course["unitIDs"]:
    unit = json.loads((course_dir / "units" / f"{unit_id}.json").read_text())
    for lesson_id in unit["lessonIDs"]:
        lesson = json.loads((course_dir / "lessons" / f"{lesson_id}.json").read_text())
        check = "compiled port challenge" if lesson["exerciseKind"] == "runnable" else "quick check"
        lines.append(f"## {lesson['title']} (`{lesson_id}`, {check})")
        lines.append(f"Bridge rule: {lesson['writing']['rule']}")
        lines.append(f"Check: {lesson['writing']['question']}")
        for target in lesson["bridge"]["credits"]:
            target_course, target_lesson = target.split("/")
            data = json.loads((ROOT / "courses" / target_course / "lessons" / f"{target_lesson}.json").read_text())
            lines.append(f"- `{target}` — {data['title']}: {data['writing']['rule']}")
        lines.append("")
(ROOT / "editorial/bridges_20261123" / course_id / "CREDITS.md").write_text("\n".join(lines))
print(f"{course_id}: CREDITS.md written")
