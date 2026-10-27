fn palindromic_subsequence(text:&str)->usize {
    assert!(text.is_ascii()); let a=text.as_bytes(); let n=a.len(); if n==0 { return 0; } let mut dp=vec![vec![0;n];n];
    for i in (0..n).rev() { dp[i][i]=1; for j in i+1..n {
        dp[i][j]=if a[i]==a[j] { 2+if j==i+1 { 0 } else { dp[i+1][j-1] } } else { dp[i+1][j].max(dp[i][j-1]) };
    } } dp[0][n-1]
}

fn main() {
    let result = palindromic_subsequence("bbbab").to_string();
    println!("{result}");
}
