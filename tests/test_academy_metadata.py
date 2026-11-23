"""Academy metadata for AI teaching: learning paths and the teaching contract.

Neither is part of a CoursePack; both only refer to existing lesson IDs.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACADEMY = ROOT / "academy"
EXPECTED_PATHS = {"rust-from-zero", "rust-for-nodejs", "rust-for-c", "rust-for-experienced",
                  "rust-backend", "async-rust", "systems-programming", "rust-interview"}


def lesson_exists(course_id: str, lesson_id: str) -> bool:
    return (ROOT / "courses" / course_id / "lessons" / f"{lesson_id}.json").is_file()


class AcademyMetadataTests(unittest.TestCase):
    def setUp(self):
        self.paths = json.loads((ACADEMY / "learning-paths.json").read_text())

    def test_paths_point_at_existing_lessons_without_duplicates(self):
        self.assertEqual(self.paths["schemaVersion"], 1)
        self.assertEqual({path["id"] for path in self.paths["paths"]}, EXPECTED_PATHS)
        for path in self.paths["paths"]:
            with self.subTest(path=path["id"]):
                self.assertRegex(path["id"], r"^[a-z0-9-]+$")
                for key in ("title", "audience", "description"):
                    self.assertTrue(path[key].strip())
                steps = [(step["courseId"], step["lessonId"]) for step in path["steps"]]
                self.assertGreaterEqual(len(steps), 10)
                self.assertEqual(len(steps), len(set(steps)))
                for course_id, lesson_id in steps:
                    self.assertTrue(lesson_exists(course_id, lesson_id), f"{course_id}/{lesson_id}")

    def test_bridge_paths_start_with_the_bridge_and_skip_what_it_credits(self):
        for path_id, course_id in (("rust-for-nodejs", "rust-for-nodejs-developers"),
                                   ("rust-for-c", "rust-for-c-developers")):
            path = next(item for item in self.paths["paths"] if item["id"] == path_id)
            course = json.loads((ROOT / "courses" / course_id / "course.json").read_text())
            bridge_ids, credited = [], set()
            for unit_id in course["unitIDs"]:
                unit = json.loads((ROOT / "courses" / course_id / "units" / f"{unit_id}.json").read_text())
                for lesson_id in unit["lessonIDs"]:
                    bridge_ids.append(lesson_id)
                    lesson = json.loads((ROOT / "courses" / course_id / "lessons" / f"{lesson_id}.json").read_text())
                    credited |= set(lesson["bridge"]["credits"])
            steps = [f"{step['courseId']}/{step['lessonId']}" for step in path["steps"]]
            self.assertEqual(steps[:len(bridge_ids)], [f"{course_id}/{lesson_id}" for lesson_id in bridge_ids])
            self.assertFalse(credited & set(steps), path_id)

    def test_teaching_contract_is_versioned_and_keeps_progress_honest(self):
        text = (ACADEMY / "teaching-contract.md").read_text()
        self.assertRegex(text, r"Version \d+\.\d+\.\d+")
        for phrase in ("AI reviewed", "revealSolution", "Do not assume what the learner has completed",
                       "Only the Crabrix app"):
            self.assertIn(phrase, text)
        self.assertFalse(re.search(r"\bverified passed\b", text, re.I))


if __name__ == "__main__":
    unittest.main()
