fn closest(points: &[(i32, i32)], k: usize) -> Vec<(i32, i32)> {
    let mut heap = std::collections::BinaryHeap::new();
    for &(x, y) in points {
        let distance = i64::from(x) * i64::from(x) + i64::from(y) * i64::from(y);
        heap.push((distance, x, y));
        if heap.len() > k {
            heap.pop();
        }
    }
    let mut selected = heap.into_vec();
    selected.sort_unstable();
    selected.into_iter().map(|(_, x, y)| (x, y)).collect()
}

fn main() {
    let result = closest(&[(1, 3), (-2, 2), (2, -2), (5, 1)], 2)
        .iter()
        .map(|(x, y)| format!("{x}:{y}"))
        .collect::<Vec<_>>()
        .join(",");
    println!("{result}");
}
