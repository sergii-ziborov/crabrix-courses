"""Academy metadata for AI teaching: learning paths, the teaching contract, Playground
practice copies and the AI Learning State schema.

None of it is part of a CoursePack; all of it only refers to existing lesson IDs.
"""
import glob
import hashlib
import json
import re
import sys
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
                       "Only the Crabrix app", "never write or edit it", "never removes any",
                       "never overwrites the learner's saved drafts"):
            self.assertIn(phrase, text)
        self.assertFalse(re.search(r"\bverified passed\b", text, re.I))


class PracticeStarterTests(unittest.TestCase):
    """academy/practice-starters.json: compiled by tools/practice_starters.py (needs rustc with
    wasm32-wasip1); here we check it still matches the lesson text without compiling."""

    def setUp(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import practice_starters
        self.tool = practice_starters
        self.data = json.loads((ACADEMY / "practice-starters.json").read_text())

    def test_every_starter_is_the_current_lesson_text_unchanged(self):
        self.assertEqual(self.data["schemaVersion"], 1)
        seen = set()
        for item in self.data["starters"]:
            key = (item["courseId"], item["lessonId"])
            with self.subTest(lesson="/".join(key)):
                self.assertNotIn(key, seen)
                seen.add(key)
                path = ROOT / "courses" / item["courseId"] / "lessons" / f"{item['lessonId']}.json"
                lesson = json.loads(path.read_text())
                self.assertFalse(lesson.get("playgroundProject"), "lessons with a project keep it")
                self.assertNotEqual(item["courseId"], "algorithms")
                self.assertIn(item["source"], ("practiceCode", "exampleCode"))
                self.assertIn(item["wrap"], (None, "main-added", "in-main"))
                self.assertIn(item["check"], ("compiles", "fails-by-design"))
                code = lesson["writing"][item["source"]]
                self.assertEqual(hashlib.sha256(code.encode()).hexdigest(), item["sha256"],
                                 "lesson text changed: run tools/practice_starters.py")
                program = self.tool.program(code, item["wrap"])
                self.assertEqual(hashlib.sha256(program.encode()).hexdigest(), item["programSha256"])
                if item["wrap"] == "in-main":
                    lines = [line[4:] if line else line for line in program.split("\n")[1:-2]]
                    self.assertEqual("\n".join(lines), code.rstrip(), "the lesson text is kept verbatim")
                else:
                    self.assertTrue(program.startswith(code.rstrip()), "the lesson text is kept verbatim")
                if item["check"] == "fails-by-design":
                    self.assertIn(lesson["exerciseKind"], self.tool.REPAIR_KINDS)

    def test_wrapping_only_adds_a_main(self):
        self.assertEqual(self.tool.program("struct A;", "main-added"), "struct A;\n\nfn main() {}\n")
        self.assertEqual(self.tool.program("let x = 1;\n\nprintln!(\"{x}\");\n", "in-main"),
                         "fn main() {\n    let x = 1;\n\n    println!(\"{x}\");\n}\n")
        self.assertEqual(self.tool.program("fn main() {}", None), "fn main() {}")


class LearningStateSchemaTests(unittest.TestCase):
    def test_schema_is_v1_and_every_academy_id_fits_it(self):
        schema = json.loads((ACADEMY / "learning-state.schema.json").read_text())
        self.assertEqual(schema["properties"]["format"]["const"], "crabrix.ai-learning-state")
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], 1)
        self.assertEqual(schema["properties"]["officialProgress"]["oneOf"][1]["properties"]["source"]["enum"],
                         ["crabrix-ios", "crabrix-backup-file"])
        pattern = re.compile(schema["$defs"]["id"]["pattern"])
        for file in glob.glob(str(ROOT / "courses" / "*" / "lessons" / "*.json")):
            lesson_id = json.loads(Path(file).read_text())["id"]
            self.assertRegex(lesson_id, pattern)
        paths = json.loads((ACADEMY / "learning-paths.json").read_text())["paths"]
        for path in paths:
            self.assertRegex(path["id"], schema["properties"]["learningPath"]["pattern"])


if __name__ == "__main__":
    unittest.main()
