fn knapsack(weights: &[usize], values: &[i32], capacity: usize) -> i32 {
    assert_eq!(weights.len(), values.len());
    let mut dp = vec![0; capacity + 1];
    for (&weight, &value) in weights.iter().zip(values) {
        for c in (weight..=capacity).rev() {
            dp[c] = dp[c].max(dp[c - weight] + value);
        }
    }
    dp[capacity]
}

fn main() {
    let result = knapsack(&[1, 3, 4, 5], &[1, 4, 5, 7], 7).to_string();
    println!("{result}");
}
