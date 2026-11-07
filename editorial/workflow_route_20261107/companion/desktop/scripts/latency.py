"""Record real GET latency and failures; nearest-rank p95 never hides the error rate."""
import argparse,concurrent.futures,json,math,time,urllib.error,urllib.request,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8080/tasks');p.add_argument('--requests',type=int,default=100);p.add_argument('--concurrency',type=int,default=4);p.add_argument('--out',type=Path,default=Path('latency.json'));a=p.parse_args()
if not 1<=a.requests<=10000 or not 1<=a.concurrency<=16:p.error('Use 1..10000 requests and 1..16 workers.')
prefix='latency-'+uuid.uuid4().hex[:8]
def sample(index):
 request_id=f'{prefix}-{index}';start=time.perf_counter_ns()
 try:
  request=urllib.request.Request(a.url,headers={'X-Request-ID':request_id})
  with urllib.request.urlopen(request,timeout=2) as response:
   status=response.status;body=response.read(65537)
   if len(body)>65536:raise ValueError('response limit')
  error=None
 except urllib.error.HTTPError as failure:status=failure.code;error=f'HTTP {status}'
 except (OSError,ValueError) as failure:status=None;error=type(failure).__name__
 return {'request_id':request_id,'status':status,'elapsed_ns':time.perf_counter_ns()-start,'error':error}
with concurrent.futures.ThreadPoolExecutor(max_workers=a.concurrency) as pool:rows=list(pool.map(sample,range(a.requests)))
passed=sorted(r['elapsed_ns'] for r in rows if r['error'] is None and 200<=r['status']<300)
report={'unit':'ns','concurrency':a.concurrency,'requests':a.requests,'failures':a.requests-len(passed),'p95_successful_only':passed[math.ceil(.95*len(passed))-1] if passed else None,'samples':rows}
a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='samples'}))
