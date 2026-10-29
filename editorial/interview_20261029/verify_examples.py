"""Execute complete std examples, and verify expected diagnostics separately."""
import json,subprocess,hashlib,re,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'build/interview-20261029';out.mkdir(parents=True,exist_ok=True)
new=set(json.load(open(Path(__file__).with_name('added-ids.json'))));rows=[]
# Explicit failures are part of the teaching contract; they must fail for the named reason.
expected={'q-ownership':'E0382','q-borrowing':'E0502','q-lifetimes':'E0515','q-send-sync':'E0277','q-future-send':'cannot be sent between threads safely','q-async-locks':'cannot be sent between threads safely'}
def check(item):
 id,field,code=item;directory=out/(id+'-'+field);directory.mkdir(exist_ok=True);source=directory/'main.rs';source.write_text(code)
 compile=subprocess.run(['rustc','--edition','2024',str(source),'-o',str(directory/'run')],text=True,capture_output=True)
 failure=expected.get(id) if field=='practiceCode' else None
 if failure:ok=compile.returncode!=0 and failure in compile.stderr;kind='expected diagnostic';run=None
 else:
  kind='complete Rust program';run=subprocess.run([str(directory/'run')],text=True,capture_output=True,timeout=5) if compile.returncode==0 else None;ok=compile.returncode==0 and run.returncode==0
 (directory/'compile.txt').write_text(compile.stderr)
 return {'id':id,'field':field,'kind':kind,'passed':ok,'codeSHA256':hashlib.sha256(code.encode()).hexdigest(),'compileExit':compile.returncode,'runExit':run.returncode if run else None,'expectedDiagnostic':failure}
items=[];context=[]
for p in sorted((ROOT/'courses/interview/lessons').glob('*.json')):
 lesson=json.loads(p.read_text())
 for field in ['exampleCode','practiceCode']:
  code=lesson['writing'][field]
  if 'fn main()' in code:
   if lesson['id']=='q-debugging-session' and field=='practiceCode':context.append({'id':lesson['id'],'field':field,'reason':'deliberate division-by-zero demonstration; do not run as a successful example'});continue
   items.append((lesson['id'],field,code))
  else:context.append({'id':lesson['id'],'field':field,'reason':'labelled conceptual, SQL, dependency or declaration context; not a standalone std program'})
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(check,items))
for id in new:assert any(r['id']==id and r['field']=='exampleCode' and r['passed'] for r in rows),id
result={'compiler':subprocess.check_output(['rustc','-V'],text=True).strip(),'edition':'2024','scope':'desktop source correctness; not a physical-device or WASI compatibility claim','checks':rows,'contextualBlocks':context,'passed':all(r['passed'] for r in rows)}
Path(__file__).with_name('example-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print({'checks':len(rows),'pass':sum(r['passed'] for r in rows),'contextual':len(context)})
for r in rows:
 if not r['passed']:print('FAIL',r['id'],r['field'],r['compileExit'],r['runExit'])
assert result['passed']
