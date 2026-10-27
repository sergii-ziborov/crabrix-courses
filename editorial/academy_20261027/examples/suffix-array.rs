fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn suffix_array(text: &str) -> Vec<usize> {
    let n = text.len();
    let mut order: Vec<_> = (0..n).collect();
    let mut rank: Vec<i32> = text.bytes().map(i32::from).collect();
    let mut width = 1;
    while width < n {
        order.sort_unstable_by_key(|&i| (rank[i], rank.get(i + width).copied().unwrap_or(-1)));
        let mut next = vec![0; n];
        for i in 1..n {
            let (a, b) = (order[i - 1], order[i]);
            let key = |j: usize| (rank[j], rank.get(j + width).copied().unwrap_or(-1));
            next[b] = next[a] + i32::from(key(a) != key(b));
        }
        rank = next;
        if n == 0 || rank[order[n - 1]] == n as i32 - 1 {
            break;
        }
        width *= 2;
    }
    order // comparison-sort doubling: O(n log² n), byte indexes
}

fn main() {
    let result = csv(suffix_array("banana"));
    println!("{result}");
}
