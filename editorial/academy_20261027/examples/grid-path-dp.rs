fn grid_paths(rows: usize, cols: usize) -> u64 {
    if rows == 0 || cols == 0 {
        return 0;
    }
    let mut dp = vec![1; cols];
    for _ in 1..rows {
        for c in 1..cols {
            dp[c] += dp[c - 1];
        }
    }
    dp[cols - 1]
}

fn main() {
    let result = grid_paths(3, 4).to_string();
    println!("{result}");
}
