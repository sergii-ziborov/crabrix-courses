fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn semicolon<T: std::fmt::Display>(a: Vec<Vec<T>>) -> String {
    a.into_iter().map(csv).collect::<Vec<_>>().join(";")
}
fn subsets_in_mask_order(values: &[i32]) -> Vec<Vec<i32>> {
    assert!(values.len() < usize::BITS as usize);
    (0..1_usize << values.len())
        .map(|mask| {
            values
                .iter()
                .enumerate()
                .filter_map(|(i, &x)| (mask >> i & 1 == 1).then_some(x))
                .collect()
        })
        .collect()
}

fn main() {
    let result = semicolon(subsets_in_mask_order(&[1, 2]));
    println!("{result}");
}
