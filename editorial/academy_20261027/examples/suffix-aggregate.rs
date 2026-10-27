fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn suffix_maxima(values: &[i32]) -> Vec<i32> {
    let mut result = vec![0; values.len()];
    let mut high = i32::MIN;
    for i in (0..values.len()).rev() { high = high.max(values[i]); result[i] = high; }
    result
}

fn main() {
    let result = csv(suffix_maxima(&[3,1,5,2]));
    println!("{result}");
}
