fn fewest_coins(coins:&[usize],amount:usize)->i32 {
    assert!(coins.iter().all(|&c|c>0)); let mut dp=vec![amount+1;amount+1]; dp[0]=0;
    for total in 1..=amount { for &coin in coins { if coin<=total { dp[total]=dp[total].min(dp[total-coin]+1); } } }
    if dp[amount]>amount { -1 } else { dp[amount] as i32 }
}

fn main() {
    let result = fewest_coins(&[1,2,5],11).to_string();
    println!("{result}");
}
