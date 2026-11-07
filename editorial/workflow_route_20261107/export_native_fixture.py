"""Export private verification fixtures for the companion native QA target only."""
import argparse,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
labs=json.loads((HERE/'lab-contracts.json').read_text());source=[];expected=[]
for i,lab in enumerate(l for l in labs if l['profile']=='std-v1'):
 harness=lab['harness'].replace('mod solution;','mod solution {\n'+lab['reference']+'\n}').replace('fn main()','pub fn verify()',1)
 source.append(f'mod lab_{i} {{\n{harness}\n}}');expected.append(lab['expectedOutput'])
source.append('fn main(){'+''.join(f'lab_{i}::verify();' for i in range(20))+'}')
companion={p.relative_to(HERE/'companion/local').as_posix():p.read_text() for p in (HERE/'companion/local').rglob('*') if p.is_file() and not any(part in {'target','__pycache__'} for part in p.relative_to(HERE/'companion/local').parts)}
value={'standardSource':'\n'.join(source),'standardExpected':''.join(expected),'sql':[l for l in labs if l['profile']=='sqlite-v1'],'companion':companion}
args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(value,indent=2)+'\n')
