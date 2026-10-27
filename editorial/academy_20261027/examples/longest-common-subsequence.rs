fn lcs(a: &str, b: &str) -> usize {
    assert!(a.is_ascii() && b.is_ascii());
    let mut dp = vec![vec![0; b.len() + 1]; a.len() + 1];
    for (i, x) in a.bytes().enumerate() {
        for (j, y) in b.bytes().enumerate() {
            dp[i + 1][j + 1] = if x == y {
                dp[i][j] + 1
            } else {
                dp[i][j + 1].max(dp[i + 1][j])
            };
        }
    }
    dp[a.len()][b.len()]
}

fn main() {
    let result = lcs("abcde", "ace").to_string();
    println!("{result}");
}
