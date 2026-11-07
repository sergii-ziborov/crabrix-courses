"""Bounded client retries for the idempotent readiness GET; never retries writes."""
import argparse,json,random,time,urllib.error,urllib.request,uuid
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8080/ready');p.add_argument('--attempts',type=int,default=3);p.add_argument('--deadline',type=float,default=1.5);a=p.parse_args()
if not 1<=a.attempts<=8 or not .1<=a.deadline<=10:p.error('Use 1..8 attempts and a .1..10 second total budget.')
request_id='retry-'+uuid.uuid4().hex[:12];deadline=time.monotonic()+a.deadline;rows=[];ready=False
for attempt in range(1,a.attempts+1):
 remaining=deadline-time.monotonic()
 if remaining<.1:break
 status=None;transient=True
 try:
  request=urllib.request.Request(a.url,headers={'X-Request-ID':request_id})
  with urllib.request.urlopen(request,timeout=min(.5,remaining)) as response:status=response.status;response.read(65536)
  ready=status==200;transient=False
 except urllib.error.HTTPError as failure:status=failure.code;transient=status in {429,502,503,504}
 except OSError:pass
 rows.append({'attempt':attempt,'request_id':request_id,'status':status,'transient':transient})
 if ready or not transient or attempt==a.attempts:break
 delay=random.uniform(0,min(.2,.05*2**(attempt-1)))
 if delay+.1>deadline-time.monotonic():break
 time.sleep(delay)
print(json.dumps({'ready':ready,'attempts':rows,'maximum_attempts':a.attempts,'deadline_seconds':a.deadline}))
raise SystemExit(0 if ready else 2)
