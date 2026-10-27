fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn primes_to(n: usize) -> Vec<usize> {
    let mut prime = vec![true; n + 1];
    prime[0] = false;
    if n >= 1 {
        prime[1] = false;
    }
    let mut p = 2;
    while p <= n / p {
        if prime[p] {
            for multiple in (p * p..=n).step_by(p) {
                prime[multiple] = false;
            }
        }
        p += 1;
    }
    (2..=n).filter(|&i| prime[i]).collect()
}

fn main() {
    let result = csv(primes_to(30));
    println!("{result}");
}
