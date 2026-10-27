fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn semicolon<T:std::fmt::Display>(a:Vec<Vec<T>>)->String { a.into_iter().map(csv).collect::<Vec<_>>().join(";") }
fn strongly_connected(graph:&[Vec<usize>])->Vec<Vec<usize>> {
    fn finish(v:usize,g:&[Vec<usize>],seen:&mut [bool],order:&mut Vec<usize>) {
        seen[v]=true; for &u in &g[v] { if !seen[u] { finish(u,g,seen,order); } } order.push(v);
    }
    fn collect(v:usize,g:&[Vec<usize>],seen:&mut [bool],group:&mut Vec<usize>) {
        seen[v]=true; group.push(v); for &u in &g[v] { if !seen[u] { collect(u,g,seen,group); } }
    }
    let n=graph.len(); let mut reverse=vec![Vec::new();n];
    for (v,ns) in graph.iter().enumerate() { for &u in ns { reverse[u].push(v); } }
    let mut seen=vec![false;n]; let mut order=Vec::new();
    for v in 0..n { if !seen[v] { finish(v,graph,&mut seen,&mut order); } }
    seen.fill(false); let mut groups=Vec::new();
    for v in order.into_iter().rev() { if !seen[v] { let mut group=Vec::new(); collect(v,&reverse,&mut seen,&mut group); group.sort_unstable(); groups.push(group); } }
    groups.sort(); groups
}

fn main() {
    let result = semicolon(strongly_connected(&[vec![1],vec![2],vec![0,3],vec![4],vec![3]]));
    println!("{result}");
}
