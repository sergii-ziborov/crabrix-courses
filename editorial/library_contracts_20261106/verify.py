"""Run unchanged external consumers, real Cargo profiles and graded-lab negatives."""
import hashlib,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
OUT=ROOT/'build/library-contracts-20261106';OUT.mkdir(parents=True,exist_ok=True)
LABS=json.loads((HERE/'lab-contracts.json').read_text());RECORDS=[]
def run(cmd,cwd=None,ok=True,output=None):
 p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True,timeout=90)
 success=p.returncode==0
 if success!=ok:raise AssertionError(f'{cmd}: expected success={ok}\n{p.stdout[-1500:]}\n{p.stderr[-2500:]}')
 if output is not None and p.stdout!=output:raise AssertionError(f'{cmd}: stdout {p.stdout!r} != {output!r}')
 return p

def compile_run(source,toolchain,name,extra=(),expect=True,output=None):
 folder=OUT/name;folder.mkdir(parents=True,exist_ok=True);src=folder/'main.rs';src.write_text(source);bin=folder/'program';p=run(['rustup','run',toolchain,'rustc','--edition=2021',*extra,str(src),'-o',str(bin)],ok=expect)
 if expect:return run([str(bin)],output=output)
 return p

versions={t:run(['rustup','run',t,'rustc','--version']).stdout.strip() for t in ['1.78','stable']}
for t in versions:
 for lab in LABS:
  folder=OUT/f'{t}-{lab["id"]}';folder.mkdir(parents=True,exist_ok=True);(folder/'main.rs').write_text(lab['harness'])
  row={'id':lab['id'],'toolchain':versions[t],'contractSHA256':hashlib.sha256(json.dumps({k:lab[k] for k in ['reference','starter','mutant','harness']},sort_keys=True).encode()).hexdigest(),'cases':[]}
  # Forged text does not repair the behavior required by the separate caller.
  forged=lab['mutant'];match=re.search(r'pub fn [^{]+\{',forged)
  if match:forged=forged[:match.end()]+' println!(\"PASS '+lab['id']+'\"); '+forged[match.end():]
  else:raise AssertionError('forge insertion point')
  for name,source,passes in [('reference',lab['reference'],True),('unchanged',lab['starter'],False),('wrong',lab['mutant'],False),('forgedVerdict',forged,False)]:
   (folder/'solution.rs').write_text(source);binary=folder/name
   run(['rustup','run',t,'rustc','--edition=2021',str(folder/'main.rs'),'-o',str(binary)])
   p=run([str(binary)],ok=passes,output=lab['expectedOutput'] if passes else None)
   row['cases'].append({'kind':name,'compiled':True,'passed':p.returncode==0})
  RECORDS.append(row)
 for lid in [l['id'] for l in LABS]:
  lesson=json.loads((ROOT/'courses/projects/lessons'/f'{lid}.json').read_text());compile_run(lesson['writing']['exampleCode'],t,f'{t}-reading-{lid}')

# An unchanged downstream file is linked separately to each candidate rlib.
consumer='''extern crate retry_policy;
fn main() {
    assert!(retry_policy::RetryPolicy::new(0).is_none());
    for n in [1u8, 3, 255] {
        assert_eq!(retry_policy::RetryPolicy::new(n).unwrap().attempts(), n);
    }
    println!("unchanged consumer passed");
}
'''
v1='''pub struct RetryPolicy { attempts: u8 }
impl RetryPolicy {
    pub fn new(attempts: u8) -> Option<Self> {
        if attempts == 0 { None } else { Some(Self { attempts }) }
    }
    pub fn attempts(&self) -> u8 { self.attempts }
}
'''
v2=LABS[0]['reference'];consumer_path=HERE/'fixtures/unchanged-consumer.rs';consumer_path.parent.mkdir(parents=True,exist_ok=True);consumer_path.write_text(consumer)
api=[]
for t in versions:
 for name,source,result in [('v1',v1,'pass'),('v2',v2,'pass'),('broken-arity',v2.replace('new(attempts: u8)','new(attempts: u8, delay_ms: u32)'),'compile-fail'),('broken-behavior',LABS[0]['mutant'],'run-fail')]:
  folder=OUT/f'{t}-api-{name}';folder.mkdir(parents=True,exist_ok=True);lib=folder/'lib.rs';lib.write_text(source);rlib=folder/'libretry_policy.rlib';run(['rustup','run',t,'rustc','--edition=2021','--crate-type=lib','--crate-name=retry_policy',str(lib),'-o',str(rlib)])
  bin=folder/'consumer';p=run(['rustup','run',t,'rustc','--edition=2021',str(consumer_path),'--extern',f'retry_policy={rlib}','-o',str(bin)],ok=result!='compile-fail')
  if result!='compile-fail':run([str(bin)],ok=result=='pass',output='unchanged consumer passed\n' if result=='pass' else None)
  api.append({'compiler':versions[t],'candidate':name,'observed':result})

# Same optional-limit behavior, deliberately requiring the newer std method.
newer='''fn permits(value: Option<u16>, ceiling: u16) -> bool { value.is_none_or(|n| n > 0 && n <= ceiling) }
fn main() { assert!(permits(None, 0)); assert!(!permits(Some(0), 7)); println!("same behavior"); }
'''
msrv=[]
for t in versions:
 p=compile_run(newer,t,f'{t}-too-new-method',expect=t!='1.78',output='same behavior\n' if t!='1.78' else None)
 if t=='1.78':assert 'E0599' in p.stderr
 msrv.append({'compiler':versions[t],'isNoneOr':'compile-fail E0599' if t=='1.78' else 'passed'})

workspace=HERE/'fixtures/feature-matrix';workspace.mkdir(parents=True,exist_ok=True)
def put(name,text):
 p=workspace/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
put('Cargo.toml','[workspace]\nresolver = "2"\nmembers = ["api", "consumer", "edge-minimal", "edge-default", "graph"]\n')
put('api/Cargo.toml','[package]\nname = "compat_api"\nversion = "1.1.0"\nedition = "2021"\nrust-version = "1.78"\n[features]\ndefault = ["pretty"]\npretty = []\ndetails = []\ntrace = []\n')
lib='''pub fn label(id: u16) -> String { format!("core={id}") }
#[cfg(feature = "details")]
pub fn details(id: u16) -> String { format!("{}; details", label(id)) }
#[cfg(feature = "trace")]
pub fn trace(id: u16) -> String { format!("trace: {}", label(id)) }
pub fn requested() -> (bool, bool, bool) {
    (cfg!(feature = "pretty"), cfg!(feature = "details"), cfg!(feature = "trace"))
}
'''
put('api/src/lib.rs',lib)
put('consumer/Cargo.toml','[package]\nname = "unchanged_consumer"\nversion = "0.1.0"\nedition = "2021"\nrust-version = "1.78"\n[features]\ndefault = ["compat_api/default"]\ndetails = ["compat_api/details"]\ntrace = ["compat_api/trace"]\n[dependencies]\ncompat_api = { path = "../api", default-features = false }\n')
client='''fn main() {
    for n in [0, 7, 42, u16::MAX] { assert_eq!(compat_api::label(n), format!("core={n}")); }
    #[cfg(feature = "details")]
    assert_eq!(compat_api::details(7), "core=7; details");
    #[cfg(feature = "trace")]
    assert_eq!(compat_api::trace(7), "trace: core=7");
    println!("core=7");
}
'''
put('consumer/src/main.rs',client)
for edge,defaults,feature in [('edge-minimal',False,'details'),('edge-default',True,'trace')]:
 put(edge+'/Cargo.toml',f'[package]\nname = "{edge.replace("-","_")}"\nversion = "0.1.0"\nedition = "2021"\nrust-version = "1.78"\n[dependencies]\ncompat_api = {{ path = "../api", default-features = {str(defaults).lower()}, features = ["{feature}"] }}\n')
 put(edge+'/src/lib.rs','pub fn observed() -> (bool,bool,bool) { compat_api::requested() }\n')
put('graph/Cargo.toml','[package]\nname = "feature_graph"\nversion = "0.1.0"\nedition = "2021"\nrust-version = "1.78"\n[dependencies]\nedge_minimal = { path = "../edge-minimal" }\nedge_default = { path = "../edge-default" }\n')
put('graph/src/main.rs','fn main() { assert_eq!(edge_minimal::observed(), (true,true,true)); assert_eq!(edge_default::observed(), (true,true,true)); println!("merged=pretty,details,trace"); }\n')
# This fixture deliberately retains lockfile format 3 for the stated minimum Cargo.
lock=workspace/'Cargo.lock'
if lock.exists():lock.unlink()
run(['rustup','run','1.78','cargo','generate-lockfile','--offline','--manifest-path',str(workspace/'Cargo.toml')])
assert 'version = 3' in lock.read_text().split('[[package]]')[0]
cargo=[]
env=os.environ.copy();env['CARGO_TARGET_DIR']=str(OUT/'cargo-target');env['CARGO_NET_OFFLINE']='true'
def cargo_run(t,flags=(),ok=True,package='unchanged_consumer',stdout=None):
 cmd=['rustup','run',t,'cargo','run','--quiet','--locked','--offline','--manifest-path',str(workspace/'Cargo.toml'),'-p',package,*flags]
 p=subprocess.run(cmd,env=env,text=True,capture_output=True,timeout=90)
 if (p.returncode==0)!=ok:raise AssertionError(f'{cmd}\n{p.stderr[-3000:]}')
 if stdout is not None:assert p.stdout==stdout,(cmd,p.stdout)
 return p
profiles=[('default',[]),('minimal',['--no-default-features']),('details',['--no-default-features','--features','details']),('trace',['--no-default-features','--features','trace']),('union',['--no-default-features','--features','details,trace'])]
try:
 for t in versions:
  for name,flags in profiles:cargo_run(t,flags,stdout='core=7\n');cargo.append({'compiler':versions[t],'profile':name,'passed':True})
  cargo_run(t,package='feature_graph',stdout='merged=pretty,details,trace\n');cargo.append({'compiler':versions[t],'profile':'two-path-default-union','passed':True})
  put('api/src/lib.rs',lib.replace('format!("core={id}")','if cfg!(feature = "details") { format!("changed={id}") } else { format!("core={id}") }',1))
  cargo_run(t,['--no-default-features','--features','details'],ok=False);cargo.append({'compiler':versions[t],'mutant':'feature-changes-baseline','rejected':True})
  duplicate=lib+'\n#[cfg(feature="details")] fn backend() {}\n#[cfg(feature="trace")] fn backend() {}\n';put('api/src/lib.rs',duplicate)
  cargo_run(t,['--no-default-features','--features','details'],stdout='core=7\n');cargo_run(t,['--no-default-features','--features','trace'],stdout='core=7\n');p=cargo_run(t,['--no-default-features','--features','details,trace'],ok=False);assert 'E0428' in p.stderr;cargo.append({'compiler':versions[t],'mutant':'duplicate-only-in-union','individualProfilesPass':True,'unionRejected':True})
  put('api/src/lib.rs',lib)
finally:put('api/src/lib.rs',lib)
report={'toolchains':versions,'labs':RECORDS,'unchangedConsumerSHA256':hashlib.sha256(consumer.encode()).hexdigest(),'consumerSourceUnchanged':consumer_path.read_text()==consumer,'apiConsumers':api,'msrvNegative':msrv,'cargoMatrix':cargo,'readingPrograms':{'passed':6,'failed':0},'limits':['Desktop compiler/Cargo evidence, not physical-device evidence.','Local lesson harnesses grade API behavior; they do not claim to emulate an old compiler or every Cargo feature profile.','Finite consumers and configurations do not prove all downstream compatibility.']}
(HERE/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Verified: 6 reading runs, 24 lab runs, 8 API consumer cases, real MSRV negative and Cargo feature matrix')
