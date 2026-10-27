fn longest_k_distinct(values: &[i32], k: usize) -> usize {
    let mut counts = std::collections::HashMap::new();
    let (mut left, mut best) = (0, 0);
    for (right, &x) in values.iter().enumerate() {
        *counts.entry(x).or_insert(0) += 1;
        while counts.len() > k {
            let old = values[left];
            let count = counts.get_mut(&old).unwrap();
            *count -= 1;
            if *count == 0 {
                counts.remove(&old);
            }
            left += 1;
        }
        best = best.max(right + 1 - left);
    }
    best
}

fn main() {
    let result = longest_k_distinct(&[1, 2, 1, 2, 3, 2, 2], 2).to_string();
    println!("{result}");
}
