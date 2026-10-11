"""Regression checks for lesson code markup and Atlas answer reveals."""

import json
import hashlib
import unittest
from pathlib import Path


COURSES = Path(__file__).resolve().parents[1] / "courses"


class EditorialQualityTests(unittest.TestCase):
    def test_every_example_has_its_own_packaged_infographic(self):
        root = COURSES / "examples"
        projects = sorted((root / "library-projects").glob("*/project.json"))
        self.assertEqual(len(projects), 46)
        paths, hashes = set(), set()
        for metadata in projects:
            project = json.loads(metadata.read_text(encoding="utf-8"))
            with self.subTest(example=project["id"]):
                illustration = project.get("illustration")
                self.assertIsNotNone(illustration)
                expected = f"media/{project['id']}.png"
                self.assertEqual(illustration["path"], expected)
                self.assertTrue(illustration["alt"].strip())
                self.assertTrue(illustration["caption"].strip())
                image = (root / expected).read_bytes()
                self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
                width = int.from_bytes(image[16:20], "big")
                height = int.from_bytes(image[20:24], "big")
                self.assertGreaterEqual(width, 800)
                self.assertGreaterEqual(height, 500)
                paths.add(expected)
                hashes.add(hashlib.sha256(image).hexdigest())
        self.assertEqual(len(hashes), 46, "Each example needs a distinct teaching image")
        self.assertEqual(paths, {p.relative_to(root).as_posix() for p in (root / "media").glob("*")})

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
