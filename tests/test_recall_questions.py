import json, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RecallQuestionTests(unittest.TestCase):
    """Flashcards ask authored questions about each lesson, never a generic "core idea"."""

    def test_every_lesson_has_its_own_recall_questions(self):
        lessons = [p for p in sorted((ROOT / 'courses').glob('*/lessons/*.json')) if p.parts[-3] != 'examples']
        self.assertEqual(len(lessons), 798)
        for path in lessons:
            writing = json.loads(path.read_text())['writing']
            recall = writing.get('recall', [])
            self.assertEqual(len(recall), 1 if path.parts[-3] == 'algorithms' else 2, path.name)
            questions = [card['question'] for card in recall]
            self.assertEqual(len(set(questions)), len(questions), path.name)
            for card in recall:
                self.assertNotIn('core idea', card['question'].lower(), path.name)
                self.assertNotEqual(card['question'].strip(), writing['question'].strip(), path.name)
                self.assertLessEqual(len(card['answer']), 400, path.name)
                self.assertLessEqual(len(card.get('code', '').splitlines()), 12, path.name)


if __name__ == '__main__':
    unittest.main()
