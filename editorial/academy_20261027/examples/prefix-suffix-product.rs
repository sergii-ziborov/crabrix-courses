fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn products_except_self(values: &[i64]) -> Vec<i64> {
    let mut result = vec![1; values.len()];
    let mut product = 1;
    for i in 0..values.len() {
        result[i] = product;
        product *= values[i];
    }
    product = 1;
    for i in (0..values.len()).rev() {
        result[i] *= product;
        product *= values[i];
    }
    result
}

fn main() {
    let result = csv(products_except_self(&[1, 2, 3, 4]));
    println!("{result}");
}
