fn choose(n: u64, k: u64) -> u64 {
    if k > n {
        return 0;
    }
    assert!(n <= 60);
    let k = k.min(n - k);
    let mut answer = 1_u128;
    for i in 1..=k {
        answer = answer * (n - k + i) as u128 / i as u128;
    }
    answer as u64
}

fn main() {
    let result = choose(20, 6).to_string();
    println!("{result}");
}
