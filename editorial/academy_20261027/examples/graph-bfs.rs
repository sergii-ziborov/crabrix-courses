fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn edge_distances(graph: &[Vec<usize>], start: usize) -> Vec<i32> {
    let mut distance = vec![-1; graph.len()];
    let mut queue = std::collections::VecDeque::from([start]);
    distance[start] = 0;
    while let Some(v) = queue.pop_front() {
        for &u in &graph[v] {
            if distance[u] == -1 {
                distance[u] = distance[v] + 1;
                queue.push_back(u);
            }
        }
    }
    distance
}

fn main() {
    let result = csv(edge_distances(
        &[vec![1, 2], vec![0, 3], vec![0, 4], vec![1], vec![2]],
        0,
    ));
    println!("{result}");
}
