fn balloon_coins(values:&[i32])->i32 {
    let mut a=vec![1]; a.extend_from_slice(values); a.push(1); let n=a.len(); let mut dp=vec![vec![0;n];n];
    for width in 2..n { for left in 0..n-width { let right=left+width;
        for last in left+1..right { dp[left][right]=dp[left][right].max(dp[left][last]+dp[last][right]+a[left]*a[last]*a[right]); }
    } } dp[0][n-1]
}

fn main() {
    let result = balloon_coins(&[3,1,5,8]).to_string();
    println!("{result}");
}
