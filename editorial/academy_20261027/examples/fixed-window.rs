fn greatest_k_sum(values: &[i32], k: usize) -> i32 {
    assert!(k > 0 && k <= values.len());
    let mut sum: i32 = values[..k].iter().sum();
    let mut best = sum;
    for i in k..values.len() {
        sum += values[i] - values[i - k];
        best = best.max(sum);
    }
    best
}

fn main() {
    let result = greatest_k_sum(&[2, 1, 5, 1, 3, 2], 3).to_string();
    println!("{result}");
}
