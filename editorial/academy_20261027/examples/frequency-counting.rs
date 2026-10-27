fn mode(values: &[i32]) -> i32 {
    let mut counts = std::collections::HashMap::new();
    for &x in values { *counts.entry(x).or_insert(0) += 1; }
    *counts.iter().min_by_key(|&(x, count)| (-*count, *x)).unwrap().0
}

fn main() {
    let result = mode(&[4,2,4,3,2,4]).to_string();
    println!("{result}");
}
