fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn z_values(text: &str) -> Vec<usize> {
    let a = text.as_bytes();
    let n = a.len();
    let mut z = vec![0; n];
    let (mut left, mut right) = (0, 0);
    for i in 1..n {
        if i < right {
            z[i] = z[i - left].min(right - i);
        }
        while i + z[i] < n && a[z[i]] == a[i + z[i]] {
            z[i] += 1;
        }
        if i + z[i] > right {
            left = i;
            right = i + z[i];
        }
    }
    z // convention: z[0] is zero
}

fn main() {
    let result = csv(z_values("aabcaabxaaaz"));
    println!("{result}");
}
