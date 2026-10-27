fn travelling_salesman(cost: &[Vec<i32>]) -> i32 {
    let n = cost.len();
    assert!(n > 0 && n <= 16);
    let states = 1 << n;
    let infinity = i32::MAX / 4;
    let mut dp = vec![vec![infinity; n]; states];
    dp[1][0] = 0;
    for mask in 1..states {
        for last in 0..n {
            if dp[mask][last] == infinity {
                continue;
            }
            for next in 0..n {
                if mask >> next & 1 == 0 {
                    let new = mask | 1 << next;
                    dp[new][next] = dp[new][next].min(dp[mask][last] + cost[last][next]);
                }
            }
        }
    }
    (0..n)
        .map(|last| dp[states - 1][last] + cost[last][0])
        .min()
        .unwrap()
}

fn main() {
    let result = travelling_salesman(&[
        vec![0, 10, 15, 20],
        vec![10, 0, 35, 25],
        vec![15, 35, 0, 30],
        vec![20, 25, 30, 0],
    ])
    .to_string();
    println!("{result}");
}
