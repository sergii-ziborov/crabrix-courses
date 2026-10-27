fn component_count(graph:&[Vec<usize>])->usize {
    let mut seen=vec![false;graph.len()]; let mut count=0;
    for start in 0..graph.len() {
        if seen[start] { continue; } count+=1; seen[start]=true; let mut stack=vec![start];
        while let Some(v)=stack.pop() { for &u in &graph[v] { if !seen[u] { seen[u]=true; stack.push(u); } } }
    }
    count
}

fn main() {
    let result = component_count(&[vec![1],vec![0,2],vec![1],vec![4],vec![3],vec![]]).to_string();
    println!("{result}");
}
