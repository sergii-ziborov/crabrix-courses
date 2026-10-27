fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn rolling_matches(text: &str, pattern: &str) -> Vec<usize> {
    let (a, p) = (text.as_bytes(), pattern.as_bytes());
    let m = p.len();
    if m == 0 {
        return (0..=a.len()).collect();
    }
    if m > a.len() {
        return Vec::new();
    }
    let (base, modulus) = (257_u64, 1_000_000_007_u64);
    let mut power = 1;
    for _ in 1..m {
        power = power * base % modulus;
    }
    let (mut wanted, mut hash) = (0, 0);
    for i in 0..m {
        wanted = (wanted * base + p[i] as u64) % modulus;
        hash = (hash * base + a[i] as u64) % modulus;
    }
    let mut out = Vec::new();
    for i in 0..=a.len() - m {
        if hash == wanted && &a[i..i + m] == p {
            out.push(i);
        } // verify collisions
        if i + m < a.len() {
            hash = ((hash + modulus - a[i] as u64 * power % modulus) * base + a[i + m] as u64)
                % modulus;
        }
    }
    out
}

fn main() {
    let result = csv(rolling_matches("abracadabra", "abra"));
    println!("{result}");
}
