fn prim_weight(graph: &[Vec<(usize, i64)>]) -> i64 {
    if graph.is_empty() {
        return 0;
    }
    let mut seen = vec![false; graph.len()];
    let mut heap = std::collections::BinaryHeap::from([std::cmp::Reverse((0, 0))]);
    let mut total = 0;
    while let Some(std::cmp::Reverse((weight, v))) = heap.pop() {
        if seen[v] {
            continue;
        }
        seen[v] = true;
        total += weight;
        for &(u, w) in &graph[v] {
            if !seen[u] {
                heap.push(std::cmp::Reverse((w, u)));
            }
        }
    }
    assert!(seen.into_iter().all(|v| v), "connected graph required");
    total
}

fn main() {
    let result = prim_weight(&[
        vec![(1, 1), (2, 4)],
        vec![(0, 1), (2, 2), (3, 5)],
        vec![(0, 4), (1, 2), (3, 3)],
        vec![(1, 5), (2, 3)],
    ])
    .to_string();
    println!("{result}");
}
