"""Publishing regressions for the October Academy correction set."""
import json
import io
import subprocess
import sys
import tarfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'editorial/academy_20261027'))
from oracles import solve
from rust_sources import CODE
sys.path.insert(0, str(ROOT / 'tools'))
from coursepack import read_course
from recompute_digests import digest


class AcademyCorrectionsTests(unittest.TestCase):
    def test_all_patterns_have_individual_programs_and_questions(self):
        lessons = sorted((ROOT / 'courses/algorithms/lessons').glob('*.json'))
        archive = subprocess.check_output(['git', 'archive', '52b6751', 'courses/algorithms/lessons'], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as packed:
            baseline = {entry.name: json.load(packed.extractfile(entry)) for entry in packed if entry.isfile()}
        questions = set()
        for path in lessons:
            lesson = json.loads(path.read_text())
            original = baseline[path.relative_to(ROOT).as_posix()]
            with self.subTest(lesson=lesson['id']):
                self.assertEqual(lesson['writing']['correctAnswer'], original['writing']['correctAnswer'])
                self.assertEqual(lesson['algorithm']['rustSketch'], lesson['writing']['exampleCode'])
                self.assertIn('fn main()', lesson['writing']['exampleCode'])
                questions.add(lesson['writing']['question'])
        self.assertEqual(len(lessons), 600)
        self.assertEqual(len(questions), 600)
        self.assertEqual(len(CODE), 200)
        self.assertEqual(len(set(CODE.values())), 200)

    def test_expected_results_match_independent_references(self):
        paths = sorted((ROOT / 'courses/algorithms/checks').glob('*.challenge.json'))
        self.assertEqual(len(paths), 200)
        for path in paths:
            check = json.loads(path.read_text())['challenge']
            pattern = path.name.removeprefix('algorithm.').removesuffix('.challenge.json')
            cases = check['verificationCases']
            with self.subTest(pattern=pattern):
                self.assertGreaterEqual(len({c['input'].strip() for c in cases}), 5)
                self.assertGreaterEqual(len(cases), 7)
                for case in cases:
                    self.assertEqual(case['expectedAnswer'], solve(pattern, case['input'].strip()))

    def test_known_incorrect_answers_are_repaired(self):
        for pattern, expected in [('imos-sweep', '5'), ('binary-search-answer', '21')]:
            path = ROOT / f'courses/algorithms/lessons/algorithm.{pattern}.model.json'
            self.assertEqual(json.loads(path.read_text())['algorithm']['expectedAnswer'], expected)

    def test_nested_content_digests_match_authored_values(self):
        for course_id in ['algorithms', 'ownership', 'projects', 'concurrency', 'systems', 'interview']:
            course = read_course(ROOT / 'courses' / course_id)
            self.assertEqual(course['contentDigest'], digest(course), course_id)
            for unit in course['units']:
                self.assertEqual(unit['contentDigest'], digest(unit), unit['id'])
                for lesson in unit['lessons']:
                    self.assertEqual(lesson['contentDigest'], digest(lesson), lesson['id'])


if __name__ == '__main__':
    unittest.main()
