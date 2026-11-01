"""Regressions for the November Algorithm Atlas correction pass."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS = ROOT / 'editorial/academy_20261101'
sys.path.insert(0, str(PASS))
from adversarial import CASES
from atlas_overlay import solve

LESSONS = ROOT / 'courses/algorithms/lessons'
CHECKS = ROOT / 'courses/algorithms/checks'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


class AtlasPassTests(unittest.TestCase):
    def test_model_rule_does_not_contain_the_marked_answer(self):
        paths = sorted(LESSONS.glob('*.model.json'))
        self.assertEqual(len(paths), 200)
        for path in paths:
            writing = load(path)['writing']
            answer = writing['answers'][writing['correctAnswer']].rstrip('.').lower()
            with self.subTest(lesson=path.name):
                self.assertNotIn(answer, writing['rule'].lower())

    def test_challenge_summary_and_rule_do_not_reveal_the_answer(self):
        for path in sorted(LESSONS.glob('*.challenge.json')):
            lesson = load(path)
            answer = lesson['algorithm']['expectedAnswer']
            if len(answer) < 3:
                continue
            with self.subTest(lesson=path.name):
                self.assertNotIn(answer, lesson['writing']['summary'])
                self.assertNotIn(answer, lesson['writing']['rule'])

    def test_each_counterexample_is_a_private_case_with_the_oracle_answer(self):
        for pattern, text, _ in CASES:
            check = load(CHECKS / f'algorithm.{pattern}.challenge.json')['challenge']
            found = [c for c in check['verificationCases'] if c['input'] == text]
            with self.subTest(pattern=pattern, input=text):
                self.assertEqual(len(found), 1)
                self.assertEqual(found[0]['kind'], 'adversarial')
                self.assertEqual(found[0]['expectedAnswer'], solve(pattern, text))
                self.assertIn(json.dumps(text, ensure_ascii=False), check['verificationSource'])

    def test_recorded_wrong_solutions_are_all_rejected(self):
        evidence = load(PASS / 'wrong-solution-evidence.json')
        self.assertEqual(evidence['survivors'], [])
        self.assertEqual(evidence['rejectedByExtendedHarness'], evidence['wrongSolutions'])
        self.assertTrue(load(PASS / 'atlas-verification.json')['passed'])

    def test_editorial_notes_stay_out_of_lessons(self):
        for path in sorted(LESSONS.glob('*.json')):
            text = path.read_text(encoding='utf-8')
            with self.subTest(lesson=path.name):
                self.assertNotIn('previous published answer', text)
                self.assertNotIn('belongs to a different five-day example', text)


if __name__ == '__main__':
    unittest.main()
