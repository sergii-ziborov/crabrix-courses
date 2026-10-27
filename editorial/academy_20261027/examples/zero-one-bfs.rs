fn zero_one_distance(graph: &[Vec<(usize, i64)>], start: usize, goal: usize) -> i64 {
    let mut distance = vec![i64::MAX; graph.len()];
    distance[start] = 0;
    let mut deque = std::collections::VecDeque::from([(start, 0)]);
    while let Some((v, cost)) = deque.pop_front() {
        if distance[v] != cost {
            continue;
        }
        for &(u, w) in &graph[v] {
            assert!(w == 0 || w == 1);
            if cost + w < distance[u] {
                distance[u] = cost + w;
                if w == 0 {
                    deque.push_front((u, cost));
                } else {
                    deque.push_back((u, cost + 1));
                }
            }
        }
    }
    if distance[goal] == i64::MAX {
        -1
    } else {
        distance[goal]
    }
}

fn main() {
    let result = zero_one_distance(
        &[
            vec![(1, 0), (2, 1)],
            vec![(0, 0), (2, 0)],
            vec![(0, 1), (1, 0), (3, 1)],
            vec![(2, 1)],
        ],
        0,
        3,
    )
    .to_string();
    println!("{result}");
}
