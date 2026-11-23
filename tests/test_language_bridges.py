"""Bridge courses: "Rust for C Developers" and "Rust for Node.js Developers".

See editorial/bridges_20261123/SPEC.md for the authoring contract.
"""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
COURSES = ROOT / "courses"
CLI = ["python3", str(ROOT / "tools/coursepack.py")]
BRIDGES = {"rust-for-c-developers": ("c-", {"c"}),
           "rust-for-nodejs-developers": ("node-", {"javascript", "typescript"})}
CREDITABLE = {"basics", "ownership", "projects", "concurrency", "systems"}

SAMPLE_LESSON = {
    "id": "c-sample", "parentID": "c-unit", "order": 0, "title": "Sample", "concept": "A sample",
    "minutes": 9, "exerciseKind": "planned",
    "writing": {"summary": "s", "explanation": "e", "exampleCaption": "c",
                "exampleCode": "fn main() {\n    println!(\"hi\");\n}", "task": "t", "success": "s",
                "rule": "r", "practiceCode": "fn main() {}", "question": "q", "answers": ["a", "b"],
                "correctAnswer": 1, "feedback": "f",
                "recall": [{"question": "q1", "answer": "a1"}, {"question": "q2", "answer": "a2"}]},
    "depth": {"traceSteps": [{"title": "t", "detail": "d"}], "misconception": "m", "correction": "c",
              "transferChallenge": "t", "connections": []},
    "bridge": {"from": "c", "fromLabel": "C", "fromCode": "int main(void) { return 0; }",
               "fromCaption": "c", "contrasts": [{"from": "a", "rust": "b"}, {"from": "c", "rust": "d"}],
               "credits": ["basics/variables"]},
    "illustration": {"path": "media/c-sample.png", "alt": "a", "caption": "c"},
}


def lessons(course_id: str) -> list[dict]:
    course = json.loads((COURSES / course_id / "course.json").read_text())
    result = []
    for unit_id in course["unitIDs"]:
        unit = json.loads((COURSES / course_id / "units" / f"{unit_id}.json").read_text())
        for lesson_id in unit["lessonIDs"]:
            result.append(json.loads((COURSES / course_id / "lessons" / f"{lesson_id}.json").read_text()))
    return result


class BridgeValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        shutil.copytree(COURSES / "basics", self.tmp / "basics")
        root = self.tmp / "bridge-demo"
        for folder in ("units", "lessons", "checks", "media"):
            (root / folder).mkdir(parents=True)
        (root / "course.json").write_text(json.dumps({
            "id": "bridge-demo", "language": "en", "contentVersion": "1.0.0", "contentDigest": "x",
            "order": 9, "level": "FOR C DEVELOPERS", "title": "Demo", "subtitle": "Demo",
            "systemImage": "c.square.fill", "theme": "bridges", "unitIDs": ["c-unit"]}))
        (root / "units" / "c-unit.json").write_text(json.dumps({
            "id": "c-unit", "parentID": "bridge-demo", "order": 0, "level": 1, "title": "U",
            "subtitle": "U", "lessonIDs": ["c-sample"]}))
        (root / "checks" / "c-sample.json").write_text(json.dumps(
            {"evidence": {"kind": "reasoning", "correctAnswer": 1}}))
        (root / "terms.json").write_text("[]")
        (root / "provenance.json").write_text("{}")
        shutil.copyfile(COURSES / "basics" / "media" / "variables.png", root / "media" / "c-sample.png")
        self.write_lesson(SAMPLE_LESSON)

    def write_lesson(self, lesson: dict) -> None:
        (self.tmp / "bridge-demo" / "lessons" / "c-sample.json").write_text(json.dumps(lesson))

    def validate(self) -> subprocess.CompletedProcess:
        return subprocess.run(CLI + ["validate", "--courses", str(self.tmp), "--schema", str(ROOT / "schemas")],
                              cwd=ROOT, text=True, capture_output=True)

    def mutated(self, change) -> dict:
        lesson = json.loads(json.dumps(SAMPLE_LESSON))
        change(lesson)
        return lesson

    def test_valid_bridge_lesson_passes(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_malformed_bridges_are_rejected(self):
        cases = {
            "language": lambda l: l["bridge"].update({"from": "python"}),
            "unknown target": lambda l: l["bridge"].update({"credits": ["basics/no-such-lesson"]}),
            "wrong course": lambda l: l["bridge"].update({"credits": ["ownership/variables"]}),
            "interview": lambda l: l["bridge"].update({"credits": ["interview/q-ownership"]}),
            "duplicate": lambda l: l["bridge"].update({"credits": ["basics/variables", "basics/variables"]}),
            "one contrast": lambda l: l["bridge"].update({"contrasts": [{"from": "a", "rust": "b"}]}),
            "five credits": lambda l: l["bridge"].update({"credits": ["basics/variables", "basics/loops", "basics/ranges", "basics/enums", "basics/structs"]}),
            "long contrast": lambda l: l["bridge"]["contrasts"][0].update({"rust": "x" * 161}),
            "odd backticks": lambda l: l["bridge"]["contrasts"][0].update({"from": "`a"}),
            "extra field": lambda l: l["bridge"].update({"note": "x"}),
            "snippet": lambda l: l["writing"].update({"exampleCode": "let x = 1;"}),
            "long source": lambda l: l["bridge"].update({"fromCode": "x;\n" * 31}),
        }
        for name, change in cases.items():
            with self.subTest(name):
                self.write_lesson(self.mutated(change))
                self.assertNotEqual(self.validate().returncode, 0, name)

    def test_build_declares_the_bridge_capability(self):
        out = self.tmp / "dist"
        result = subprocess.run(CLI + ["build", "--courses", str(self.tmp), "--out", str(out), "--deterministic"],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        bridge = json.loads((out / "bridge-demo.descriptor.payload.json").read_text())
        basics = json.loads((out / "basics.descriptor.payload.json").read_text())
        self.assertIn("bridge-lessons-v1", bridge["requiredCapabilities"])
        self.assertNotIn("bridge-lessons-v1", basics["requiredCapabilities"])


@unittest.skipUnless(all((COURSES / course / "course.json").is_file() for course in BRIDGES),
                     "bridge courses are not authored in this checkout")
class BridgeCourseTests(unittest.TestCase):
    def test_course_metadata(self):
        for course_id in BRIDGES:
            with self.subTest(course_id):
                course = json.loads((COURSES / course_id / "course.json").read_text())
                self.assertEqual(course["id"], course_id)
                self.assertEqual(course["theme"], "bridges")
                self.assertTrue(3 <= len(course["unitIDs"]) <= 5)
                provenance = json.loads((COURSES / course_id / "provenance.json").read_text())
                self.assertEqual(provenance["editorialRevision"], "bridges_20261123")
                for unit_id in course["unitIDs"]:
                    unit = json.loads((COURSES / course_id / "units" / f"{unit_id}.json").read_text())
                    self.assertTrue(3 <= len(unit["lessonIDs"]) <= 6, unit_id)

    def test_every_lesson_is_a_complete_comparison(self):
        for course_id, (prefix, languages) in BRIDGES.items():
            items = lessons(course_id)
            runnable = sum(lesson["exerciseKind"] == "runnable" for lesson in items)
            self.assertGreaterEqual(runnable / len(items), 0.6, course_id)
            self.assertGreater(len({lesson["writing"]["correctAnswer"] for lesson in items}), 1, course_id)
            for lesson in items:
                with self.subTest(lesson=lesson["id"]):
                    self.assertTrue(lesson["id"].startswith(prefix))
                    bridge = lesson["bridge"]
                    self.assertIn(bridge["from"], languages)
                    self.assertIn("fn main()", lesson["writing"]["exampleCode"])
                    self.assertEqual(len(lesson["writing"]["recall"]), 2)
                    self.assertTrue(8 <= lesson["minutes"] <= 14)
                    self.assertEqual(lesson["illustration"]["path"], f"media/{lesson['id']}.png")
                    self.assertTrue((COURSES / course_id / lesson["illustration"]["path"]).is_file())
                    check = json.loads((COURSES / course_id / "checks" / f"{lesson['id']}.json").read_text())
                    if lesson["exerciseKind"] == "runnable":
                        self.assertEqual(check["evidence"]["kind"], "algorithmChallenge")
                        source = (COURSES / course_id / "projects" / lesson["id"] / "solution.rs").read_text()
                        self.assertEqual(source.strip(), check["challenge"]["source"].strip())
                        self.assertGreaterEqual(len(check["challenge"]["verificationCases"]), 3)
                    else:
                        self.assertEqual(check["evidence"],
                                         {"kind": "reasoning", "correctAnswer": lesson["writing"]["correctAnswer"]})

    def test_credits_point_at_real_academy_lessons_once_per_course(self):
        for course_id in BRIDGES:
            seen = set()
            for lesson in lessons(course_id):
                for target in lesson["bridge"]["credits"]:
                    with self.subTest(lesson=lesson["id"], target=target):
                        target_course, target_lesson = target.split("/")
                        self.assertIn(target_course, CREDITABLE)
                        self.assertTrue((COURSES / target_course / "lessons" / f"{target_lesson}.json").is_file())
                        self.assertNotIn(target, seen)
                        seen.add(target)

    def test_terms_refer_to_bridge_lessons(self):
        for course_id in BRIDGES:
            ids = {lesson["id"] for lesson in lessons(course_id)}
            terms = json.loads((COURSES / course_id / "terms.json").read_text())
            self.assertTrue(8 <= len(terms) <= 16, course_id)
            for term in terms:
                self.assertIn(term["topic"], ids, term)


if __name__ == "__main__":
    unittest.main()
