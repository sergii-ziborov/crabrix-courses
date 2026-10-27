fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn neighbors(n:usize,edges:&[(usize,usize)],query:usize)->Vec<usize> {
    let mut graph=vec![Vec::new();n];
    for &(a,b) in edges { graph[a].push(b); graph[b].push(a); }
    graph[query].sort_unstable(); graph[query].clone()
}

fn main() {
    let result = csv(neighbors(5,&[(0,2),(1,2),(2,4)],2));
    println!("{result}");
}
