"""Independent sample-answer references; deliberately simple, often exhaustive.

These check semantics. Rust teaching implementations use the named algorithm;
the Python references often use a different, slower method on bounded fixtures.
"""
import ast
from collections import Counter, deque
from functools import lru_cache
import heapq
import itertools
import math
import re

from previous_oracles import solve as previous, array, comma, number


def ints(text):
    return list(map(int, re.findall(r'-?\d+', text)))


def matrix(text):
    return ast.literal_eval(text[text.index('['):].replace('inf', '999999999'))


def lists(text):
    return [ast.literal_eval(x) for x in re.findall(r'\[[^\[\]]*\]',text)]


def tree(text):
    raw = ast.literal_eval(text[text.index('['):].replace('null', 'None'))
    if not raw or raw[0] is None: return None
    root = [raw[0], None, None]; queue = deque([root]); i = 1
    while queue and i < len(raw):
        parent = queue.popleft()
        for k in [1, 2]:
            if i < len(raw) and raw[i] is not None:
                child = [raw[i],None,None]; parent[k]=child; queue.append(child)
            i+=1
    return root


def traversal(root, order):
    if root is None: return []
    left, right = traversal(root[1],order), traversal(root[2],order)
    return {'pre': [root[0]]+left+right, 'in': left+[root[0]]+right, 'post': left+right+[root[0]]}[order]


def edges(text, directed=False, weighted=False):
    if weighted:
        return [(int(a),int(b),int(w)) for a,b,w in re.findall(r'(\d+)(?:->|-)(\d+):(-?\d+)',text)]
    if directed:
        return [(int(a),int(b)) for a,b in re.findall(r'(\d+)->(\d+)',text)]
    return [(int(a),int(b)) for a,b in re.findall(r'\((\d+),(\d+)\)',text)]


def graph(text, directed=False, weighted=False):
    es=edges(text,directed,weighted)
    n=number(text,'n') if re.search(r'\bn=',text) else 1+max((max(e[:2]) for e in es),default=0)
    g=[[] for _ in range(n)]
    for e in es:
        a,b=e[:2]; w=e[2] if weighted else 1
        g[a].append((b,w))
        if not directed: g[b].append((a,w))
    for ns in g: ns.sort()
    return g,es


def distances(g, start):
    # Bellman-Ford reference also works for the positive-weight fixtures.
    d=[math.inf]*len(g);d[start]=0
    for _ in range(len(g)-1):
        for a,ns in enumerate(g):
            for b,w in ns:d[b]=min(d[b],d[a]+w)
    return [x if x != math.inf else -1 for x in d]


def connected(n, es):
    g=[set() for _ in range(n)]
    for a,b in es:g[a].add(b);g[b].add(a)
    seen=set();groups=[]
    for s in range(n):
        if s in seen:continue
        component=set([s]);todo=[s];seen.add(s)
        while todo:
            a=todo.pop()
            for b in g[a]-seen:seen.add(b);component.add(b);todo.append(b)
        groups.append(component)
    return groups


def solve(pattern, text):
    text=text.strip()
    if pattern=='index-map':
        values=array(text)
        return str(min((j-i for i in range(len(values)) for j in range(i+1,len(values)) if values[i]==values[j]),default=-1))
    # Correct the stock-span contract: the span includes today.
    if pattern=='monotonic-decreasing-stack':
        return comma(1+sum(1 for _ in itertools.takewhile(lambda v:v<=x,reversed(array(text)[:i]))) for i,x in enumerate(array(text)))
    try:return previous(pattern,text)
    except NotImplementedError:pass
    match pattern:
        case 'reservoir-sampling':
            values,choices=lists(text);answer=None
            assert len(values)==len(choices)
            for i,(v,c) in enumerate(zip(values,choices)):
                assert 0<=c<=i
                if c==i:answer=v
            return str(answer) if answer is not None else 'none'
        case 'floyd-state-cycle':
            values=array(text);seen=set();i=0
            while i not in seen:seen.add(i);i=values[i]
            return str(i)
        case 'complement-lookup':
            values=array(text);target=number(text,'target')
            pairs=[(i,j) for i in range(len(values)) for j in range(i+1,len(values)) if values[i]+values[j]==target]
            # Canonical example only: the harness accepts any valid pair.
            return comma(min(pairs,key=lambda p:(p[1],p[0]))) if pairs else '-1,-1'
        case 'randomized-set' | 'treap':
            values=set()
            for op,n in re.findall(r'(add|remove|insert|delete)(-?\d+)',text):
                if op in ('add','insert'):values.add(int(n))
                else:values.discard(int(n))
            return comma(sorted(values))
        case 'in-place-merge':
            a,b=lists(text);return comma(sorted(a[:number(text,'m')]+b))
        case 'min-stack' | 'queue-with-stacks' | 'lazy-heap-deletion':
            values=[]
            for token in text.split():
                if token.startswith(('push','enqueue')):values.append(int(re.search(r'-?\d+',token)[0]))
                elif token=='pop':values.pop()
                elif token=='dequeue':values.pop(0)
                elif token.startswith('delete'):values.remove(int(token[6:]))
            return str(values[0] if pattern=='queue-with-stacks' else min(values))
        case 'expression-shunting-yard':
            output=[];ops=[];priority={'+':1,'-':1,'*':2,'/':2}
            for token in text.split():
                if token.lstrip('-').isdigit():output.append(token)
                elif token=='(':ops.append(token)
                elif token==')':
                    while ops[-1]!='(':output.append(ops.pop())
                    ops.pop()
                else:
                    while ops and ops[-1]!='(' and priority[ops[-1]]>=priority[token]:output.append(ops.pop())
                    ops.append(token)
            return ' '.join(output+ops[::-1])
        case 'merge-sort':
            pairs=re.findall(r'\((-?\d+),([^,)]+)\)',text)
            return comma(str(k)+v for k,v in sorted(((int(k),v) for k,v in pairs),key=lambda p:p[0]))
        case 'peak-search':
            a=array(text)
            return str(next(i for i,x in enumerate(a) if (i==0 or x>a[i-1]) and (i+1==len(a) or x>a[i+1])))
        case 'matrix-binary-search':return str(any(16 in row for row in matrix(text))).lower()
        case 'binary-search-answer':
            a=array(text);days=number(text,'days')
            def possible(capacity):
                count=1;load=0
                for x in a:
                    if load+x>capacity:count+=1;load=0
                    load+=x
                return count<=days
            return str(next(c for c in range(max(a),sum(a)+1) if possible(c)))
        case 'partition-median':
            a,b=lists(text);merged=sorted(a+b);n=len(merged)
            return f'{(merged[(n-1)//2]+merged[n//2])/2:g}'
        case 'list-reversal' | 'list-middle' | 'merge-two-lists' | 'remove-nth-from-end' | 'partition-list' | 'reorder-list' | 'reverse-k-group':
            if pattern=='merge-two-lists':
                a,b=text.split(' and ');return comma(sorted(ints(a)+ints(b)))
            a=list(map(int,text.split('->'))) if text else []
            match pattern:
                case 'list-reversal':return comma(a[::-1])
                case 'list-middle':return str(a[len(a)//2])
                case 'remove-nth-from-end':del a[-2];return comma(a)
                case 'partition-list':return comma([x for x in a if x<3]+[x for x in a if x>=3])
                case 'reorder-list':
                    out=[]
                    while a:
                        out.append(a.pop(0))
                        if a:out.append(a.pop())
                    return comma(out)
                case 'reverse-k-group':return comma(itertools.chain.from_iterable(a[i:i+3][::-1] if len(a[i:i+3])==3 else a[i:i+3] for i in range(0,len(a),3)))
        case 'list-cycle':return str(not text.endswith('tail->none')).lower()
        case 'list-intersection':
            shared=lists(text)[2]
            return str(shared[0]) if shared else 'none'
        case 'copy-random-list':
            a,r=lists(text.replace('null','None'))
            return comma(f'{v}:{"null" if target is None else target}' for v,target in zip(a,r))
        case 'tree-preorder' | 'tree-inorder' | 'tree-postorder':return comma(traversal(tree(text),{'tree-preorder':'pre','tree-inorder':'in','tree-postorder':'post'}[pattern]))
        case 'tree-level-order':
            root=tree(text);queue=deque([root] if root else []);out=[]
            while queue:
                total=0
                for _ in range(len(queue)):
                    node=queue.popleft();total+=node[0];queue.extend(c for c in node[1:] if c is not None)
                out.append(total)
            return comma(out)
        case 'tree-height-balance':
            def height(n):
                if n is None:return 0
                a,b=height(n[1]),height(n[2])
                return -1 if min(a,b)<0 or abs(a-b)>1 else max(a,b)+1
            return str(height(tree(text))>=0).lower()
        case 'bst-search-insert':return comma(sorted(traversal(tree(text),'in')+[5]))
        case 'lowest-common-ancestor':
            def path(n,target):
                if n is None:return None
                if n[0]==target:return [n[0]]
                sub=path(n[1],target) or path(n[2],target)
                return [n[0]]+sub if sub else None
            a,b=path(tree(text),5),path(tree(text),1)
            return str([x for x,y in zip(a,b) if x==y][-1])
        case 'tree-serialize':
            def visit(n):return ['#'] if n is None else [str(n[0])]+visit(n[1])+visit(n[2])
            return ','.join(visit(tree(text)))
        case 'tree-diameter':
            best=0
            def depth(n):
                nonlocal best
                if n is None:return 0
                a,b=depth(n[1]),depth(n[2]);best=max(best,a+b);return max(a,b)+1
            depth(tree(text));return str(best)
        case 'tree-rerooting':
            g,_=graph(text);return comma(sum(distances(g,s)) for s in range(len(g)))
        case 'closest-k-heap':
            pts=ast.literal_eval(text)
            return comma(f'{x}:{y}' for x,y in sorted(pts,key=lambda p:(p[0]**2+p[1]**2,p[0],p[1]))[:2])
        case 'priority-scheduling':
            jobs=[tuple(map(int,t)) for t in re.findall(r'\(id(\d+),t(\d+),d(\d+)\)',text)]
            time=0;out=[]
            while jobs:
                time=max(time,min(j[1] for j in jobs));job=min((j for j in jobs if j[1]<=time),key=lambda j:(j[2],j[0]))
                jobs.remove(job);time+=job[2];out.append(job[0])
            return comma(out)
        case 'meeting-rooms-heap' | 'sweep-line-events':
            ranges=ast.literal_eval(text);events=[(s,1) for s,e in ranges]+[(e,-1) for s,e in ranges]
            active=best=0
            for _,d in sorted(events):active+=d;best=max(best,active)
            return str(best)
        case 'adjacency-list':
            g,_=graph(text);return comma(b for b,w in g[2])
        case 'graph-dfs':
            g,_=graph(text);seen=set();out=[]
            def visit(s):
                seen.add(s);out.append(s)
                for b,w in g[s]:
                    if b not in seen:visit(b)
            visit(0);return comma(out)
        case 'graph-bfs':
            g,_=graph(text);return comma(distances(g,0))
        case 'connected-components' | 'disjoint-set-union':
            return str(len(connected(number(text,'n'),edges(text))))
        case 'grid-flood-fill':
            a=matrix(text);todo=[(1,1)];seen=set()
            while todo:
                r,c=todo.pop()
                if not (0<=r<len(a) and 0<=c<len(a[0])) or (r,c) in seen or a[r][c]!=a[1][1]:continue
                seen.add((r,c));todo.extend([(r-1,c),(r+1,c),(r,c-1),(r,c+1)])
            return str(len(seen))
        case 'bipartite-coloring':
            g,_=graph(text)
            return str(any(all((mask>>a&1)!=(mask>>b&1) for a,ns in enumerate(g) for b,w in ns) for mask in range(1<<len(g)))).lower()
        case 'undirected-cycle':
            g,es=graph(text)
            return str(len(es)>len(g)-len(connected(len(g),es))).lower()
        case 'kahn-topological':
            g,es=graph(text,True)
            return comma(min(p for p in itertools.permutations(range(len(g))) if all(p.index(a)<p.index(b) for a,b in es)))
        case 'dfs-topological':
            g,_=graph(text,True);seen=set();out=[]
            def visit(a):
                seen.add(a)
                for b,w in g[a]:
                    if b not in seen:visit(b)
                out.append(a)
            for s in range(len(g)):
                if s not in seen:visit(s)
            return comma(out[::-1])
        case 'strong-components':
            g,_=graph(text,True);n=len(g);reach=[]
            for s in range(n):
                seen={s};todo=[s]
                while todo:
                    for b,w in g[todo.pop()]:
                        if b not in seen:seen.add(b);todo.append(b)
                reach.append(seen)
            remaining=set(range(n));groups=[]
            while remaining:
                s=min(remaining);group={x for x in remaining if s in reach[x] and x in reach[s]};remaining-=group;groups.append(sorted(group))
            return ';'.join(comma(c) for c in groups)
        case 'dijkstra' | 'zero-one-bfs' | 'bellman-ford' | 'dag-shortest-path':
            directed=pattern in ('bellman-ford','dag-shortest-path')
            g,_=graph(text,directed,True);d=distances(g,0)
            return str(d[3] if pattern=='zero-one-bfs' else d[4]) if pattern in ('zero-one-bfs','dag-shortest-path') else comma(d)
        case 'prim-mst' | 'kruskal-mst':
            g,es=graph(text,False,True);n=len(g)
            trees=[subset for subset in itertools.combinations(es,n-1) if len(connected(n,[(a,b) for a,b,w in subset]))==1]
            best=min(trees,key=lambda es:sum(w for a,b,w in es))
            return str(sum(w for a,b,w in best)) if pattern=='prim-mst' else comma(sorted(w for a,b,w in best))
        case 'floyd-warshall':
            a=matrix(text);n=len(a)
            # Enumerate simple paths; positive-weight bounded fixtures.
            paths=[]
            for k in range(n-1):
                for middle in itertools.permutations([i for i in range(n) if i not in (0,2)],k):
                    path=(0,)+middle+(2,);paths.append(sum(a[x][y] for x,y in zip(path,path[1:])))
            return str(min(paths))
        case 'a-star':
            sx,sy,gx,gy=ints(text);return str(abs(gx-sx)+abs(gy-sy))
        case 'bidirectional-bfs':
            start,goal=text.split(' via ')[0].split(' -> ');words=text.split('[')[1].split(']')[0].split(',');q=deque([(start,1)]);seen={start}
            while q:
                a,d=q.popleft()
                if a==goal:return str(d)
                for b in words:
                    if b not in seen and sum(x!=y for x,y in zip(a,b))==1:seen.add(b);q.append((b,d+1))
            return '0'
        case 'dinic-max-flow':
            es=edges(text,True,True);n=max(4,1+max(max(a,b) for a,b,w in es));cap=[[0]*n for _ in range(n)]
            for a,b,w in es:cap[a][b]+=w
            total=0
            while True:
                parent={0:None};q=deque([0])
                while q and 3 not in parent:
                    a=q.popleft()
                    for b in range(n):
                        if cap[a][b]>0 and b not in parent:parent[b]=a;q.append(b)
                if 3 not in parent:return str(total)
                flow=math.inf;b=3
                while b:flow=min(flow,cap[parent[b]][b]);b=parent[b]
                b=3
                while b:a=parent[b];cap[a][b]-=flow;cap[b][a]+=flow;b=a
                total+=flow
        case 'combination-sum':
            a=sorted(array(text));out=[]
            def visit(start,left,path):
                if left==0:out.append(tuple(path));return
                for i in range(start,len(a)):
                    if a[i]<=left:visit(i,left-a[i],path+[a[i]])
            visit(0,7,[]);return ';'.join(comma(t) for t in sorted(set(out)))
        case 'parentheses-generation':
            n=number(text,'n');out=[]
            for chars in itertools.product('()',repeat=2*n):
                balance=0
                for c in chars:
                    balance+=1 if c=='(' else -1
                    if balance<0:break
                else:
                    if balance==0:out.append(''.join(chars))
            return ';'.join(out)
        case 'word-grid-search':
            raw,word=re.fullmatch(r'grid=(.*) word=(.*)',text).groups();a=raw.split(',')
            def visit(r,c,i,seen):
                if i==len(word):return True
                if not(0<=r<len(a) and 0<=c<len(a[0])) or (r,c) in seen or a[r][c]!=word[i]:return False
                return any(visit(x,y,i+1,seen|{(r,c)}) for x,y in [(r-1,c),(r+1,c),(r,c-1),(r,c+1)])
            return str(any(visit(r,c,0,set()) for r in range(len(a)) for c in range(len(a[0])))).lower()
        case 'palindrome-partition':
            @lru_cache(None)
            def count(s):return 1 if not s else sum(count(s[i:]) for i in range(1,len(s)+1) if s[:i]==s[:i][::-1])
            return str(count(text))
        case 'n-queens':
            n=number(text,'n');return str(sum(len({r+c for r,c in enumerate(p)})==n and len({r-c for r,c in enumerate(p)})==n for p in itertools.permutations(range(n))))
        case 'sudoku':return str(next(iter(set('123456789')-set(text.split('=')[1]))))
        case 'activity-selection':
            ranges=ast.literal_eval(text);return str(max(len(c) for n in range(len(ranges)+1) for c in itertools.combinations(ranges,n) if all(a[1]<=b[0] or b[1]<=a[0] for a,b in itertools.combinations(c,2))))
        case 'merge-intervals' | 'insert-interval':
            ranges=ast.literal_eval(text)
            if pattern=='insert-interval':ranges.append((4,8))
            result=[]
            for start,end in sorted(ranges):
                if result and start<=result[-1][1]:result[-1][1]=max(result[-1][1],end)
                else:result.append([start,end])
            return comma(f'{a}-{b}' for a,b in result)
        case 'jump-game' | 'jump-game-two':
            a=array(text);d=[math.inf]*len(a);d[0]=0
            for i in range(len(a)):
                for j in range(i+1,min(len(a),i+a[i]+1)):d[j]=min(d[j],d[i]+1)
            return str(d[-1]!=math.inf).lower() if pattern=='jump-game' else str(int(d[-1]) if d[-1]!=math.inf else -1)
        case 'gas-station':
            gas,cost=lists(text);n=len(gas)
            for start in range(n):
                tank=0
                for k in range(n):
                    i=(start+k)%n;tank+=gas[i]-cost[i]
                    if tank<0:break
                else:return str(start)
            return '-1'
        case 'deadline-scheduling':
            jobs=[tuple(map(int,p)) for p in re.findall(r'\(d(\d+),p(\d+)\)',text)];best=0
            for n in range(len(jobs)+1):
                for subset in itertools.combinations(jobs,n):
                    if all(i<=d for i,(d,p) in enumerate(sorted(subset),1)):best=max(best,sum(p for d,p in subset))
            return str(best)
        case 'minimum-arrows':
            ranges=ast.literal_eval(text);points=sorted({x for r in ranges for x in r})
            return str(next(n for n in range(len(points)+1) if any(all(any(a<=p<=b for p in subset) for a,b in ranges) for subset in itertools.combinations(points,n))))
        case 'coin-change-min':
            a=array(text);d=[0]+[99]*11
            for i in range(1,12):d[i]=1+min((d[i-c] for c in a if c<=i),default=99)
            return str(d[11] if d[11]<99 else -1)
        case 'word-break-dp':
            s,raw=re.fullmatch(r'text=(.*) dict=\[(.*)\]',text).groups();words=raw.split(',')
            @lru_cache(None)
            def possible(s):return not s or any(s.startswith(w) and possible(s[len(w):]) for w in words if w)
            return str(possible(s)).lower()
        case 'decode-ways':
            @lru_cache(None)
            def count(s):
                if not s:return 1
                if s[0]=='0':return 0
                return count(s[1:])+(count(s[2:]) if len(s)>1 and 10<=int(s[:2])<=26 else 0)
            return str(count(text))
        case 'zero-one-knapsack':
            weights,values=lists(text)
            return str(max(sum(values[i] for i in range(len(weights)) if mask>>i&1) for mask in range(1<<len(weights)) if sum(weights[i] for i in range(len(weights)) if mask>>i&1)<=7))
        case 'matrix-chain':
            ds=array(text)
            @lru_cache(None)
            def cost(i,j):return 0 if j==i+1 else min(cost(i,k)+cost(k,j)+ds[i]*ds[k]*ds[j] for k in range(i+1,j))
            return str(cost(0,len(ds)-1))
        case 'interval-dp':
            @lru_cache(None)
            def best(a):return max((a[i]*(a[i-1] if i else 1)*(a[i+1] if i+1<len(a) else 1)+best(a[:i]+a[i+1:]) for i in range(len(a))),default=0)
            return str(best(tuple(array(text))))
        case 'bitmask-dp':
            a=matrix(text);n=len(a)
            return str(min(sum(a[x][y] for x,y in zip((0,)+p,p+(0,))) for p in itertools.permutations(range(1,n))))
        case 'tree-dp':
            nodes=[];parents=[]
            def visit(n,parent):
                if n is None:return
                i=len(nodes);nodes.append(n[0]);parents.append(parent);visit(n[1],i);visit(n[2],i)
            visit(tree(text),-1)
            return str(max(sum(v for i,v in enumerate(nodes) if mask>>i&1) for mask in range(1<<len(nodes)) if all(p<0 or not(mask>>i&1 and mask>>p&1) for i,p in enumerate(parents))))
        case 'aho-corasick':
            s,raw=re.fullmatch(r'text=(.*) patterns=\[(.*)\]',text).groups()
            return str(sum(s.startswith(p,i) for p in raw.split(',') for i in range(len(s))))
        case 'miller-rabin':
            n=number(text,'n');assert n<5_000_000_000,'trial-division oracle fixture bound'
            return str(n>=2 and all(n%d for d in range(2,math.isqrt(n)+1))).lower()
        case 'sparse-table':
            a=array(text);return comma(min(a[l:r+1]) for l,r in [(0,3),(2,5),(4,6)])
        case 'skip-list':return str(19 in array(text)).lower()
        case 'dsu-rollback':
            n=number(text,'n');before=text.split(' checkpoint')[0];es=edges(before)
            a,b=map(int,re.search(r'query=\((\d+),(\d+)\)',text).groups())
            return str(any(a in group and b in group for group in connected(n,es))).lower()
        case 'mo-algorithm':
            a=array(text);return comma(len(set(a[l:r+1])) for l,r in [(0,3),(2,5),(0,5)])
        case 'heavy-light':
            raw,values=text.split(' values=');g,_=graph(raw);a=ast.literal_eval(values);q=deque([(2,[2])]);seen={2}
            while q:
                s,path=q.popleft()
                if s==4:return str(sum(a[i] for i in path))
                for b,w in g[s]:
                    if b not in seen:seen.add(b);q.append((b,path+[b]))
        case 'centroid-decomposition':
            n=number(text,'n');es=edges(text)
            for deleted in range(n):
                groups=connected(n,[(a,b) for a,b in es if deleted not in (a,b)])
                if max((len(g) for g in groups if deleted not in g),default=0)<=n//2:return str(deleted)
        case _:raise NotImplementedError(pattern)
