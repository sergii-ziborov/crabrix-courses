#!/usr/bin/env python3
"""Execute actual packaged harnesses with typed fixture adapters.

Adapters trim and dispatch known fixture inputs to the real Rust algorithms.
They are test infrastructure, not example general-purpose input parsers.
"""
import json
from pathlib import Path
import re
import subprocess
from fixtures import call,r
from rust_sources import CODE,HELPERS
from verify_examples import CSV,SEMI

BASE=Path(__file__).resolve().parent;REPO=BASE.parents[1]
WORK=REPO/'build/academy-20261027/harnesses';WORK.mkdir(parents=True,exist_ok=True)
modules=[];records=[]
for id,code in CODE.items():
    check=json.loads((REPO/'courses/algorithms/checks'/f'algorithm.{id}.challenge.json').read_text())['challenge']
    cases=check['verificationCases'];unique=list(dict.fromkeys(c['input'].strip() for c in cases))
    expressions=[call(id,text) for text in unique]
    helpers=''.join(h for word,h in HELPERS.items() if re.search(r'\b'+word+r'\b',code))
    fmt=(CSV+SEMI) if any('semicolon(' in x for x in expressions) else CSV if any('csv(' in x for x in expressions) else ''
    adapter='pub fn solve(input: &str) -> String { match input.trim() {\n'+',\n'.join(r(text)+'=>'+expr for text,expr in zip(unique,expressions))+', _=>panic!("fixture adapter has no parser for unseen input") } }\n'
    actual=check['verificationSource'].replace('mod solution;','',1).replace('fn main()','fn run_actual_harness()',1)
    invalid_cases=',\n'.join('('+r(c['input'])+','+r(c['expectedAnswer'])+')' for c in cases)
    extra=''
    if id=='complement-lookup':extra='#[test] fn alternate_valid_pair() { assert!(valid("[6,4,9,7] target=13","0,3","1,2")); assert!(valid("[6,4,9,7] target=13","3,0","1,2")); assert!(!valid("[5,5] target=10","0,0","0,1")); }'
    if id=='peak-search':extra='#[test] fn alternate_peak() { assert!(valid("[1,3,2,4,1]","1","3")); assert!(valid("[1,3,2,4,1]","3","1")); assert!(!valid("[1,3,2,4,1]","2","1")); }'
    modules.append('mod '+id.replace('-','_')+' {\nmod solution {\n'+helpers+fmt+code+adapter+'}\n'+actual+
      '\n#[test] fn packaged_harness_accepts() { run_actual_harness(); }\n#[test] fn corrupt_results_fail() {\nfor (input,expected) in ['+invalid_cases+'] { assert!(!valid(input,"INVALID",expected)); }\n}\n'+extra+'\n}\n')
    records.append({'pattern':id,'distinctSemanticInputs':len(unique),'harnessCalls':len(cases)})
(WORK/'all.rs').write_text('\n'.join(modules))
c=subprocess.run(['rustc','--edition=2024','--test','-A','warnings',str(WORK/'all.rs'),'-o',str(WORK/'tests')],capture_output=True,text=True)
(WORK/'compile.log').write_text(c.stdout+c.stderr)
if c.returncode:print(c.stderr[:10000]);raise SystemExit(c.returncode)
t=subprocess.run([str(WORK/'tests'),'--test-threads=1'],capture_output=True,text=True,timeout=120)
(WORK/'tests.log').write_text(t.stdout+t.stderr);print((t.stdout+t.stderr)[-3500:])
(BASE/'harness-verification.json').write_text(json.dumps({'passed':t.returncode==0,'patterns':len(records),
    'harnessCalls':sum(r['harnessCalls'] for r in records),'scope':'Actual packaged Rust harnesses; typed known-fixture adapters, not general parsers','rows':records},indent=2)+'\n')
raise SystemExit(t.returncode)
