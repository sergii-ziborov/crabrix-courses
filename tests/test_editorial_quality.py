"""Regression checks for lesson code markup and Atlas answer reveals."""

import json
import unittest
from pathlib import Path


COURSES = Path(__file__).resolve().parents[1] / "courses"


class EditorialQualityTests(unittest.TestCase):
    def test_all_lessons_have_illustrations_and_balanced_prose_code(self):
        paths = sorted(COURSES.glob("*/lessons/*.json"))
        self.assertEqual(len(paths), 742)
        for path in paths:
            lesson = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(lesson=lesson["id"]):
                self.assertTrue(lesson.get("illustration"))
                writing = lesson.get("writing", {})
                depth = lesson.get("depth", {})
                prose = [writing.get(key, "") for key in (
                    "summary", "explanation", "rule", "task", "success", "question",
                    "feedback", "exampleCaption")]
                prose += [depth.get(key, "") for key in (
                    "misconception", "correction", "transferChallenge")]
                prose += [step["detail"] for step in depth.get("traceSteps", [])]
                for field in prose:
                    self.assertEqual(field.count("`") % 2, 0)

    def test_atlas_challenge_does_not_reveal_expected_answer_in_prose(self):
        paths = sorted((COURSES / "algorithms" / "lessons").glob("*.challenge.json"))
        self.assertEqual(len(paths), 200)
        for path in paths:
            lesson = json.loads(path.read_text(encoding="utf-8"))
            answer = f"`{lesson['algorithm']['expectedAnswer']}`"
            with self.subTest(lesson=lesson["id"]):
                self.assertNotIn(answer, lesson["writing"]["explanation"])
                for step in lesson["depth"]["traceSteps"]:
                    self.assertNotIn(answer, step["detail"])


if __name__ == "__main__":
    unittest.main()
