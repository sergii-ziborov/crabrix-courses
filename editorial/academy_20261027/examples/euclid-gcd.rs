fn gcd(mut a: u64, mut b: u64) -> u64 {
    while b != 0 {
        (a, b) = (b, a % b);
    }
    a
}

fn main() {
    let result = gcd(252, 105).to_string();
    println!("{result}");
}
