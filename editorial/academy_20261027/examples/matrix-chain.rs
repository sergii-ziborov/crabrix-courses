fn matrix_chain(dimensions:&[i64])->i64 {
    assert!(dimensions.len()>=2); let n=dimensions.len()-1; let mut dp=vec![vec![0;n];n];
    for length in 2..=n { for i in 0..=n-length { let j=i+length-1; dp[i][j]=i64::MAX;
        for k in i..j { dp[i][j]=dp[i][j].min(dp[i][k]+dp[k+1][j]+dimensions[i]*dimensions[k+1]*dimensions[j+1]); }
    } } dp[0][n-1]
}

fn main() {
    let result = matrix_chain(&[10,30,5,60]).to_string();
    println!("{result}");
}
