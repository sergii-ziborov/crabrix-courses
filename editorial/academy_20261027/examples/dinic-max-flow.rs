#[derive(Clone)]
struct FlowEdge { to:usize, reverse:usize, capacity:i64 }
fn max_flow(n:usize,edges:&[(usize,usize,i64)],source:usize,sink:usize)->i64 {
    fn send(v:usize,t:usize,pushed:i64,g:&mut [Vec<FlowEdge>],level:&[i32],next:&mut [usize])->i64 {
        if v==t { return pushed; }
        while next[v]<g[v].len() {
            let i=next[v]; let edge=g[v][i].clone();
            if edge.capacity>0 && level[edge.to]==level[v]+1 {
                let sent=send(edge.to,t,pushed.min(edge.capacity),g,level,next);
                if sent>0 { g[v][i].capacity-=sent; g[edge.to][edge.reverse].capacity+=sent; return sent; }
            }
            next[v]+=1;
        }
        0
    }
    let mut graph=vec![Vec::new();n];
    for &(a,b,capacity) in edges {
        assert!(a!=b && capacity>=0); let (ra,rb)=(graph[a].len(),graph[b].len());
        graph[a].push(FlowEdge{to:b,reverse:rb,capacity}); graph[b].push(FlowEdge{to:a,reverse:ra,capacity:0});
    }
    let mut total=0;
    loop {
        let mut level=vec![-1;n]; level[source]=0; let mut queue=std::collections::VecDeque::from([source]);
        while let Some(v)=queue.pop_front() { for edge in &graph[v] { if edge.capacity>0 && level[edge.to]<0 { level[edge.to]=level[v]+1; queue.push_back(edge.to); } } }
        if level[sink]<0 { return total; } let mut next=vec![0;n];
        loop { let sent=send(source,sink,i64::MAX,&mut graph,&level,&mut next); if sent==0 { break; } total+=sent; }
    }
}

fn main() {
    let result = max_flow(4,&[(0,1,3),(0,2,2),(1,2,1),(1,3,2),(2,3,3)],0,3).to_string();
    println!("{result}");
}
