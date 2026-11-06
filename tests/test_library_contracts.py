import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REV=ROOT/'editorial/library_contracts_20261106'
class LibraryContractTests(unittest.TestCase):
 def test_old_learning_identities_and_saved_answer_positions_are_preserved(self):
  before=json.loads((REV/'previous-identities.json').read_text());course=json.loads((ROOT/'courses/projects/course.json').read_text());self.assertEqual(course['unitIDs'][:len(before['unitIDs'])],before['unitIDs'])
  for old in before['lessons']:
   lesson=json.loads((ROOT/'courses/projects/lessons'/f'{old["id"]}.json').read_text())
   for field in ['id','parentID','order']:self.assertEqual(lesson[field],old[field])
   for field in ['question','answers','correctAnswer']:self.assertEqual(lesson['writing'][field],old[field])
 def test_each_lab_has_current_independent_harness_and_rejection_evidence(self):
  refs=json.loads((REV/'lab-contracts.json').read_text());report=json.loads((REV/'verification.json').read_text());self.assertEqual(len(refs),3)
  for ref in refs:
   course=ROOT/'courses/projects';lab=json.loads((course/'checks'/f'{ref["id"]}.json').read_text())['challenge'];self.assertEqual(lab['source'],ref['starter']);self.assertEqual(lab['verificationSource'],ref['harness']);self.assertEqual((course/'projects'/ref['id']/'solution.rs').read_text(),ref['starter']);self.assertGreaterEqual(len(lab['verificationCases']),4)
   digest=hashlib.sha256(json.dumps({k:ref[k] for k in ['reference','starter','mutant','harness']},sort_keys=True).encode()).hexdigest();rows=[r for r in report['labs'] if r['id']==ref['id']];self.assertEqual(len(rows),2)
   for row in rows:
    self.assertEqual(row['contractSHA256'],digest);cases={c['kind']:c for c in row['cases']};self.assertTrue(cases['reference']['passed'])
    for key in ['unchanged','wrong','forgedVerdict']:self.assertTrue(cases[key]['compiled']);self.assertFalse(cases[key]['passed'])
 def test_real_minimum_compiler_and_feature_union_have_distinct_evidence(self):
  report=json.loads((REV/'verification.json').read_text());self.assertIn('rustc 1.78.0',report['toolchains']['1.78']);self.assertEqual(report['msrvNegative'][0]['isNoneOr'],'compile-fail E0599');self.assertEqual(report['msrvNegative'][1]['isNoneOr'],'passed');self.assertTrue(report['consumerSourceUnchanged']);self.assertEqual(hashlib.sha256((REV/'fixtures/unchanged-consumer.rs').read_bytes()).hexdigest(),report['unchangedConsumerSHA256'])
  for compiler in report['toolchains'].values():
   rows=[r for r in report['cargoMatrix'] if r['compiler']==compiler];self.assertEqual({r['profile'] for r in rows if 'profile' in r},{'default','minimal','details','trace','union','two-path-default-union'});self.assertTrue(all(r['passed'] for r in rows if 'profile' in r));self.assertTrue(all(r['rejected'] if 'rejected' in r else r['unionRejected'] for r in rows if 'mutant' in r))
