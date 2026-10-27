fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn dijkstra(graph:&[Vec<(usize,i64)>],start:usize)->Vec<i64> {
    let mut distance=vec![i64::MAX;graph.len()]; distance[start]=0;
    let mut heap=std::collections::BinaryHeap::from([std::cmp::Reverse((0,start))]);
    while let Some(std::cmp::Reverse((cost,v)))=heap.pop() {
        if cost!=distance[v] { continue; }
        for &(u,w) in &graph[v] {
            assert!(w>=0); let next=cost.checked_add(w).expect("distance fits i64");
            if next<distance[u] { distance[u]=next; heap.push(std::cmp::Reverse((next,u))); }
        }
    }
    for d in &mut distance { if *d==i64::MAX { *d=-1; } } distance
}

fn main() {
    let result = csv(dijkstra(&[vec![(1,4),(2,1)],vec![(0,4),(2,2),(3,1)],vec![(0,1),(1,2),(3,5)],vec![(1,1),(2,5)]],0));
    println!("{result}");
}
