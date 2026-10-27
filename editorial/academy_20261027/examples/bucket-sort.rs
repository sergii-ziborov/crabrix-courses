fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn bucket_sort(values: &[f64]) -> Vec<f64> {
    if values.is_empty() {
        return Vec::new();
    }
    let n = values.len();
    let mut buckets = vec![Vec::new(); n];
    for &x in values {
        assert!((0.0..1.0).contains(&x));
        buckets[(x * n as f64) as usize].push(x);
    }
    for bucket in &mut buckets {
        for i in 1..bucket.len() {
            let mut j = i;
            while j > 0 && bucket[j] < bucket[j - 1] {
                bucket.swap(j, j - 1);
                j -= 1;
            }
        }
    }
    buckets.into_iter().flatten().collect()
}

fn main() {
    let result = csv(bucket_sort(&[0.42, 0.32, 0.23, 0.52, 0.25]));
    println!("{result}");
}
