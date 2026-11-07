import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];C=ROOT/'courses/projects';REV=ROOT/'editorial/workflow_route_20261107'
class WorkflowRouteTests(unittest.TestCase):
 def test_previous_lessons_and_saved_answers_are_unchanged(self):
  previous=json.loads((REV/'previous-identities.json').read_text());course=json.loads((C/'course.json').read_text())
  self.assertEqual(course['unitIDs'][:len(previous['unitIDs'])],previous['unitIDs'])
  for old in previous['lessons']:
   self.assertEqual(json.loads((C/'lessons'/f'{old["id"]}.json').read_text()),old,old['id'])
 def test_route_has_six_ordered_units_and_independent_practice(self):
  units=[json.loads(p.read_text()) for p in (C/'units').glob('route-*.json')];self.assertEqual(len(units),6)
  labs=json.loads((REV/'lab-contracts.json').read_text());self.assertEqual(len(labs),24)
  report=json.loads((REV/'verification.json').read_text());records={r['id']:r for r in report['labs']};positions=set();profiles=[]
  for unit in sorted(units,key=lambda u:u['order']):
   self.assertEqual(len(unit['lessonIDs']),4)
   for id in unit['lessonIDs']:
    lesson=json.loads((C/'lessons'/f'{id}.json').read_text());writing=lesson['writing'];positions.add(writing['correctAnswer'])
    self.assertGreaterEqual(len(writing['explanation'].split()),180,id)
    check=json.loads((C/'checks'/f'{id}.json').read_text())['challenge'];profiles.append(check['executionProfile'])
    lab=next(l for l in labs if l['id']==id);self.assertEqual(check['verificationSource'],lab['harness']);self.assertEqual(check['source'],lab['starter'])
    self.assertEqual((C/'projects'/id/'solution.rs').read_text(),lab['starter'])
    self.assertNotIn('verificationSource',(C/'projects'/id/'workflow-companion.json').read_text())
    digest=hashlib.sha256(json.dumps({k:lab[k] for k in ['reference','starter','mutant','harness']},sort_keys=True).encode()).hexdigest()
    self.assertEqual(records[id]['contractSHA256'],digest)
    self.assertEqual({c['kind']:c['passed'] for c in records[id]['cases']},{'reference':True,'unchanged':False,'wrong':False,'forgedVerdict':False})
  self.assertEqual(positions,{0,1,2});self.assertEqual(profiles.count('sqlite-v1'),4)
 def test_terminal_dependent_pack_refuses_older_app_versions(self):
  course=json.loads((C/'course.json').read_text());self.assertEqual(course['minimumAppVersion'],'1.1.8');self.assertIn('workflow-terminal-v1',course['requiredCapabilities'])
  companion=C/'projects/route-git-review/companion'
  for name in ['src/main.rs','Cargo.toml','migrations/001.sql','README.md','desktop/Cargo.toml','desktop/Cargo.lock','desktop/Dockerfile','desktop/scripts/acceptance.py','desktop/.github/workflows/ci.yml']:
   self.assertTrue((companion/name).is_file(),name)
  self.assertFalse(any(p.name=='target' for p in companion.rglob('*')))
if __name__=='__main__':unittest.main()
