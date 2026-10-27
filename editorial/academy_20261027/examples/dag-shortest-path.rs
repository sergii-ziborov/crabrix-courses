fn dag_distance(graph:&[Vec<(usize,i64)>],start:usize,goal:usize)->i64 {
    let n=graph.len(); let mut degree=vec![0;n]; for ns in graph { for &(u,_) in ns { degree[u]+=1; } }
    let mut queue:std::collections::VecDeque<_>=(0..n).filter(|&v|degree[v]==0).collect();
    let mut distance=vec![i64::MAX;n]; distance[start]=0; let mut visited=0;
    while let Some(v)=queue.pop_front() {
        visited+=1;
        for &(u,w) in &graph[v] {
            if distance[v]!=i64::MAX { distance[u]=distance[u].min(distance[v].checked_add(w).unwrap()); }
            degree[u]-=1; if degree[u]==0 { queue.push_back(u); }
        }
    }
    assert_eq!(visited,n); if distance[goal]==i64::MAX { -1 } else { distance[goal] }
}

fn main() {
    let result = dag_distance(&[vec![(1,2),(2,4)],vec![(3,7)],vec![(3,1)],vec![(4,3)],vec![]],0,4).to_string();
    println!("{result}");
}
