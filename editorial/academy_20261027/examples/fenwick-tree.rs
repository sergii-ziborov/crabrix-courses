fn fenwick_prefix(n: usize, adds: &[(usize, i64)], query: usize) -> i64 {
    let mut bit = vec![0; n+1];
    for &(index, value) in adds {
        assert!(index > 0);
        let mut i = index;
        while i <= n { bit[i] += value; i += i & i.wrapping_neg(); }
    }
    let (mut i, mut sum) = (query, 0);
    while i > 0 { sum += bit[i]; i &= i - 1; }
    sum
}

fn main() {
    let result = fenwick_prefix(5,&[(1,5),(3,2),(4,4)],3).to_string();
    println!("{result}");
}
