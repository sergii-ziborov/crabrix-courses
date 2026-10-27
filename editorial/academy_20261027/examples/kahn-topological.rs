fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn smallest_topological(graph: &[Vec<usize>]) -> Vec<usize> {
    let mut degree = vec![0; graph.len()];
    for ns in graph {
        for &u in ns {
            degree[u] += 1;
        }
    }
    let mut ready = std::collections::BinaryHeap::new();
    for (v, &d) in degree.iter().enumerate() {
        if d == 0 {
            ready.push(std::cmp::Reverse(v));
        }
    }
    let mut out = Vec::new();
    while let Some(std::cmp::Reverse(v)) = ready.pop() {
        out.push(v);
        for &u in &graph[v] {
            degree[u] -= 1;
            if degree[u] == 0 {
                ready.push(std::cmp::Reverse(u));
            }
        }
    }
    assert_eq!(out.len(), graph.len(), "the contract requires a DAG");
    out
}

fn main() {
    let result = csv(smallest_topological(&[
        vec![1, 2],
        vec![3],
        vec![3],
        vec![],
    ]));
    println!("{result}");
}
