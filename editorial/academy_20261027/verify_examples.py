#!/usr/bin/env python3
"""Compile and run each typed Rust fixture against independent Python answers."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from fixtures import call, r
from oracles import solve
from rust_sources import CODE, HELPERS

BASE=Path(__file__).resolve().parent
REPO=BASE.parents[1]
WORK=REPO/'build/academy-20261027/verification'
CSV='fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }\n'
SEMI='fn semicolon<T:std::fmt::Display>(a:Vec<Vec<T>>)->String { a.into_iter().map(csv).collect::<Vec<_>>().join(";") }\n'

def inputs():
    result={}
    for p in (REPO/'courses/algorithms/checks').glob('*.challenge.json'):
        c=json.loads(p.read_text())['challenge'];id=c['patternID']
        result[id]=list(dict.fromkeys(x['input'].strip() for x in c['verificationCases']))
    result['list-intersection']=['a_prefix=[4,1]; b_prefix=[5,6,1]; shared=[8,4,5]',
                                 'a_prefix=[1]; b_prefix=[2]; shared=[9]']
    try:
        from extra_cases import EXTRA
        for id,more in EXTRA.items():result[id]=list(dict.fromkeys(result[id]+more))
    except ModuleNotFoundError:pass
    return result

def source(id,expression):
    code=CODE[id]
    helpers=''.join(h for word,h in HELPERS.items() if re.search(r'\b'+word+r'\b',code))
    formatting=(CSV if 'csv(' in expression or 'semicolon(' in expression else '')+(SEMI if 'semicolon(' in expression else '')
    return helpers+formatting+code+'\nfn main() {\n    let result = '+expression+';\n    println!("{result}");\n}\n'

def main():
    WORK.mkdir(parents=True,exist_ok=True);(BASE/'examples').mkdir(exist_ok=True)
    suites=[];records=[];errors=[]
    cases=inputs()
    for id,code in CODE.items():
        try:
            expressions=[call(id,text) for text in cases[id]]
            program=source(id,expressions[0]);(BASE/'examples'/f'{id}.rs').write_text(program)
            tests=[]
            for i,(text,expression) in enumerate(zip(cases[id],expressions)):
                expected=solve(id,text)
                tests.append(f'#[test] fn case_{i}() {{ assert_eq!({expression},{r(expected)},"{{}}",{r(id+" "+text)}); }}')
                records.append({'pattern':id,'input':text,'expected':expected})
            helpers=''.join(h for word,h in HELPERS.items() if re.search(r'\b'+word+r'\b',code))
            fmt=(CSV+SEMI) if any('semicolon(' in x for x in expressions) else CSV if any('csv(' in x for x in expressions) else ''
            suites.append('#[allow(dead_code)] mod '+id.replace('-','_')+' {\n'+helpers+fmt+code+'\n'+'\n'.join(tests)+'\n}\n')
        except Exception as e:errors.append({'pattern':id,'error':repr(e)})
    if errors:
        print(json.dumps(errors,indent=2));sys.exit(1)
    (WORK/'all.rs').write_text('\n'.join(suites))
    compiled=subprocess.run(['rustc','--edition=2024','--test','-A','warnings',str(WORK/'all.rs'),'-o',str(WORK/'all-tests')],capture_output=True,text=True)
    (WORK/'compile.log').write_text(compiled.stdout+compiled.stderr)
    if compiled.returncode:
        print(compiled.stderr[:14000]);sys.exit(1)
    tested=subprocess.run([str(WORK/'all-tests'),'--test-threads=3'],capture_output=True,text=True,timeout=120)
    (WORK/'tests.log').write_text(tested.stdout+tested.stderr)
    print((tested.stdout+tested.stderr)[-10000:])
    record={'patterns':len(CODE),'distinctTypedFixtures':len(records),'compiled':compiled.returncode==0,
            'passed':tested.returncode==0,'compiler':subprocess.check_output(['rustc','--version'],text=True).strip(),
            'implementationSHA256':hashlib.sha256((BASE/'rust_sources.py').read_bytes()).hexdigest(),
            'fixtures':records}
    (BASE/'example-verification.json').write_text(json.dumps(record,indent=2)+'\n')
    sys.exit(tested.returncode)

if __name__=='__main__':main()
