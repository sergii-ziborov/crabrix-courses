"""Execute each private lab caller and reject unchanged, wrong and forged solutions."""
import concurrent.futures,hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=ROOT/'build/workflow-route-20261107';OUT.mkdir(parents=True,exist_ok=True)
LABS=json.loads((HERE/'lab-contracts.json').read_text())
def run_lab(lab):
 folder=OUT/lab['id'];folder.mkdir(exist_ok=True);(folder/'main.rs').write_text(lab['harness'])
 record={'id':lab['id'],'profile':lab['profile'],'contractSHA256':hashlib.sha256(json.dumps({k:lab[k] for k in ['reference','starter','mutant','harness']},sort_keys=True).encode()).hexdigest(),'cases':[]}
 forged=re.sub(r'(pub fn [^{]+\{)',r'\1 println!("PASS '+lab['id']+r'"); ',lab['mutant'],count=1)
 env=dict(os.environ,ROUTE_SQL_RUNNER=str(HERE/'sql_runner.py'),ROUTE_SQL_DATABASE=str(folder/'test.sqlite'))
 for name,source,expected in [('reference',lab['reference'],True),('unchanged',lab['starter'],False),('wrong',lab['mutant'],False),('forgedVerdict',forged,False)]:
  database=folder/'test.sqlite'
  if database.exists():database.unlink()
  (folder/'solution.rs').write_text(source);binary=folder/name
  build=subprocess.run(['rustc','--edition=2024',str(folder/'main.rs'),'-o',str(binary)],capture_output=True,text=True,timeout=60)
  if build.returncode:raise AssertionError(lab['id']+' '+name+' failed compilation\n'+build.stderr)
  result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=25,env=env)
  passed=result.returncode==0 and result.stdout==lab['expectedOutput']
  if passed!=expected:raise AssertionError(lab['id']+' '+name+' incorrect verdict\n'+result.stdout+'\n'+result.stderr)
  record['cases'].append({'kind':name,'compiled':True,'passed':passed,'exitCode':result.returncode})
 # The independently runnable reading is a complete program.
 (folder/'reading.rs').write_text(lab['reading']);binary=folder/'reading'
 build=subprocess.run(['rustc','--edition=2024',str(folder/'reading.rs'),'-o',str(binary)],capture_output=True,text=True,timeout=60)
 if build.returncode:raise AssertionError(lab['id']+' reading failed compilation\n'+build.stderr)
 result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=15)
 if result.returncode:raise AssertionError(lab['id']+' reading failed\n'+result.stderr)
 record['readingPassed']=True;return record
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: records=list(pool.map(run_lab,LABS))
report={'compiler':subprocess.check_output(['rustc','--version'],text=True).strip(),'lessonCount':len(LABS),'labs':records,'scope':'Desktop Rust execution; SQL uses real SQLite. Native WASM qualification is separate.'}
(HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Passed',len(records),'readings and',len(records)*4,'lab variants')
