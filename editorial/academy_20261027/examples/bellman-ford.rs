fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn bellman_ford(n: usize, edges: &[(usize, usize, i64)], start: usize) -> Vec<i64> {
    let mut distance = vec![i64::MAX; n];
    distance[start] = 0;
    for _ in 1..n {
        let mut changed = false;
        for &(a, b, w) in edges {
            if distance[a] != i64::MAX && distance[a] + w < distance[b] {
                distance[b] = distance[a] + w;
                changed = true;
            }
        }
        if !changed {
            break;
        }
    }
    for &(a, b, w) in edges {
        assert!(
            distance[a] == i64::MAX || distance[a] + w >= distance[b],
            "negative cycle"
        );
    }
    distance
        .into_iter()
        .map(|d| if d == i64::MAX { -1 } else { d })
        .collect()
}

fn main() {
    let result = csv(bellman_ford(3, &[(0, 1, 4), (0, 2, 5), (1, 2, -2)], 0));
    println!("{result}");
}
