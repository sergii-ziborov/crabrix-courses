fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn kth_largest_stream(values: &[i32], k: usize) -> Vec<i32> {
    assert!(k > 0);
    let mut heap = std::collections::BinaryHeap::new();
    let mut out = Vec::new();
    for &x in values {
        heap.push(std::cmp::Reverse(x));
        if heap.len() > k {
            heap.pop();
        }
        if heap.len() == k {
            out.push(heap.peek().unwrap().0);
        }
    }
    out
}

fn main() {
    let result = csv(kth_largest_stream(&[4, 5, 8, 2, 10], 3));
    println!("{result}");
}
