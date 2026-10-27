fn bipartite(graph:&[Vec<usize>])->bool {
    let mut color=vec![None;graph.len()];
    for start in 0..graph.len() {
        if color[start].is_some() { continue; } color[start]=Some(false); let mut queue=std::collections::VecDeque::from([start]);
        while let Some(v)=queue.pop_front() {
            for &u in &graph[v] {
                if color[u]==color[v] { return false; }
                if color[u].is_none() { color[u]=Some(!color[v].unwrap()); queue.push_back(u); }
            }
        }
    }
    true
}

fn main() {
    let result = bipartite(&[vec![1,3],vec![0,2],vec![1,3],vec![0,2]]).to_string();
    println!("{result}");
}
