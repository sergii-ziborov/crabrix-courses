fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn window_means(values: &[i64], k: usize) -> Vec<i64> {
    assert!(k>0 && k<=values.len());
    let mut sum: i64=values[..k].iter().sum(); let mut result=vec![sum/k as i64];
    for i in k..values.len() { sum+=values[i]-values[i-k]; result.push(sum/k as i64); }
    result // The fixtures use nonnegative integers; division truncates.
}

fn main() {
    let result = csv(window_means(&[2,4,6,8,10],3));
    println!("{result}");
}
