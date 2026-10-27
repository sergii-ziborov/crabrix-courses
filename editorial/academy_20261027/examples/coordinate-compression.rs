fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn ranks(values: &[i32]) -> Vec<usize> {
    let mut keys = values.to_vec();
    keys.sort_unstable();
    keys.dedup();
    values
        .iter()
        .map(|x| keys.binary_search(x).unwrap())
        .collect()
}

fn main() {
    let result = csv(ranks(&[100, -5, 100, 20]));
    println!("{result}");
}
