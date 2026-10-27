fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn apply_updates(n: usize, updates: &[(usize, usize, i64)]) -> Vec<i64> {
    let mut difference = vec![0; n + 1];
    for &(left, right, delta) in updates {
        difference[left] += delta; difference[right + 1] -= delta;
    }
    let mut current = 0;
    difference[..n].iter().map(|&d| { current += d; current }).collect()
}

fn main() {
    let result = csv(apply_updates(5,&[(1,3,3),(2,4,2)]));
    println!("{result}");
}
