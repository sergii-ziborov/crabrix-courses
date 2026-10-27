fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn counting_sort(values: &[usize], maximum: usize) -> Vec<usize> {
    let mut counts = vec![0; maximum + 1];
    for &x in values {
        counts[x] += 1;
    }
    let mut out = Vec::with_capacity(values.len());
    for (x, &count) in counts.iter().enumerate() {
        out.extend(std::iter::repeat_n(x, count));
    }
    out
}

fn main() {
    let result = csv(counting_sort(&[4, 2, 2, 5, 0, 1, 4], 5));
    println!("{result}");
}
