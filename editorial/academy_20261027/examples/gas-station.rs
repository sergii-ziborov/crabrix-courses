fn starting_station(gas: &[i32], cost: &[i32]) -> i32 {
    assert_eq!(gas.len(), cost.len());
    let (mut total, mut tank, mut start) = (0, 0, 0);
    for i in 0..gas.len() {
        let net = gas[i] - cost[i];
        total += net;
        tank += net;
        if tank < 0 {
            tank = 0;
            start = i + 1;
        }
    }
    if total < 0 || gas.is_empty() {
        -1
    } else {
        start as i32
    }
}

fn main() {
    let result = starting_station(&[1, 2, 3, 4, 5], &[3, 4, 5, 1, 2]).to_string();
    println!("{result}");
}
