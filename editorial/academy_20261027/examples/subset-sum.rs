fn subset_sum(values: &[usize], target: usize) -> bool {
    let mut reachable = vec![false; target + 1];
    reachable[0] = true;
    for &x in values {
        for sum in (x..=target).rev() {
            reachable[sum] |= reachable[sum - x];
        }
    }
    reachable[target]
}

fn main() {
    let result = subset_sum(&[2, 3, 7, 8, 10], 11).to_string();
    println!("{result}");
}
