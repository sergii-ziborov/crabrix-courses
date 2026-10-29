import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class InterviewRevisionTests(unittest.TestCase):
 def test_existing_progress_identities_and_answer_indices_are_preserved(self):
  baseline=json.loads((ROOT/'editorial/interview_20261029/baseline.json').read_text())['lessons']
  course=json.loads((ROOT/'courses/interview/course.json').read_text())
  ids=[id for unit in course['unitIDs'] for id in json.loads((ROOT/'courses/interview/units'/f'{unit}.json').read_text())['lessonIDs']]
  self.assertEqual(len(ids),52);self.assertEqual(len(set(ids)),52)
  self.assertTrue(set(baseline).issubset(ids));self.assertEqual(set(ids)-set(baseline),set(json.loads((ROOT/'editorial/interview_20261029/added-ids.json').read_text())))
  for id in ids:
   lesson=json.loads((ROOT/'courses/interview/lessons'/f'{id}.json').read_text());w=lesson['writing'];check=json.loads((ROOT/'courses/interview/checks'/f'{id}.json').read_text())
   
   if check['evidence']['kind']=='reasoning':self.assertEqual(check['evidence']['correctAnswer'],w['correctAnswer'])
   self.assertEqual(len(w['answers']),len(set(w['answers'])))
   self.assertGreater(len(lesson['depth']['transferChallenge']),60)
   if id in baseline:self.assertEqual(w['correctAnswer'],baseline[id]['correctAnswer'])
 def test_complete_new_examples_and_deliberate_errors_have_actual_compiler_evidence(self):
  evidence=json.loads((ROOT/'editorial/interview_20261029/example-verification.json').read_text());self.assertTrue(evidence['passed'])
  for id in json.loads((ROOT/'editorial/interview_20261029/added-ids.json').read_text()):
   self.assertTrue(any(r['id']==id and r['field']=='exampleCode' and r['passed'] and r['runExit']==0 for r in evidence['checks']))
  for id in ['q-borrowing','q-ownership','q-future-send','q-async-locks']:
   self.assertTrue(any(r['id']==id and r['field']=='practiceCode' and r['passed'] and r['compileExit']!=0 for r in evidence['checks']))
