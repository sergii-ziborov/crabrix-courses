import json
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISION = ROOT / "editorial/practice_20261105"


class PracticalPathTests(unittest.TestCase):
    def test_existing_identity_order_questions_and_answer_indices_are_preserved(self):
        baseline = json.loads((REVISION / "baseline.json").read_text())
        self.assertEqual(len(baseline), 754)
        for lid, before in baseline.items():
            value = json.loads((ROOT / "courses" / before["course"] / "lessons" / (lid + ".json")).read_text())
            with self.subTest(lesson=lid):
                self.assertEqual(value["parentID"], before["parentID"])
                self.assertEqual(value["order"], before["order"])
                for field in ["question", "answers", "correctAnswer"]:
                    self.assertEqual(value["writing"][field], before[field])

    def test_every_lab_has_a_separate_typed_harness_and_proven_rejections(self):
        references = json.loads((REVISION / "lab-references.json").read_text())
        evidence = {r["id"]: r for r in json.loads((REVISION / "verification.json").read_text())["labs"]}
        self.assertEqual(len(references), 31)
        for ref in references:
            root = ROOT / "courses" / ref["course"]
            check = json.loads((root / "checks" / (ref["id"] + ".json")).read_text())["challenge"]
            starter = (root / "projects" / ref["id"] / "solution.rs").read_text()
            self.assertEqual(starter, ref["starter"])
            self.assertEqual(check["verificationSource"], ref["harness"])
            self.assertNotIn("fn main", starter)
            self.assertGreaterEqual(len(check["verificationCases"]), 3)
            result = evidence[ref["id"]]
            contract = {key: ref[key] for key in ["source", "starter", "harness", "mutant"]}
            self.assertEqual(result["contractSHA256"], hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest())
            self.assertTrue(result["reference"]["passed"], ref["id"])
            for kind in ["unchanged", "wrong", "forgedVerdict"]:
                self.assertTrue(result[kind]["compiled"], ref["id"])
                self.assertFalse(result[kind]["passed"], ref["id"])

    def test_all_seventeen_new_readings_have_real_compiler_evidence(self):
        evidence = json.loads((REVISION / "reading-verification.json").read_text())["checks"]
        self.assertEqual(len(evidence), 17)
        self.assertTrue(all(record["passed"] for record in evidence))
        for lid in ["serde-roundtrip-validation", "joinset-task-ownership", "semaphore-backpressure", "graceful-shutdown-protocol"]:
            course = "projects" if lid.startswith("serde") else "concurrency"
            lesson = json.loads((ROOT / "courses" / course / "lessons" / (lid + ".json")).read_text())
            self.assertEqual(lesson["exerciseKind"], "planned")
            self.assertIn("Desktop Cargo profile", lesson["writing"]["explanation"])
