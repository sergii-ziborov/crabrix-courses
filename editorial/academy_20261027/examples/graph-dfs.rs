fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn dfs_order(graph:&[Vec<usize>],start:usize)->Vec<usize> {
    fn visit(v:usize,g:&[Vec<usize>],seen:&mut [bool],out:&mut Vec<usize>) {
        seen[v]=true; out.push(v);
        for &u in &g[v] { if !seen[u] { visit(u,g,seen,out); } }
    }
    let mut sorted=graph.to_vec(); for ns in &mut sorted { ns.sort_unstable(); }
    let mut out=Vec::new(); visit(start,&sorted,&mut vec![false;graph.len()],&mut out); out
}

fn main() {
    let result = csv(dfs_order(&[vec![1,2],vec![0,3],vec![0,4],vec![1],vec![2]],0));
    println!("{result}");
}
