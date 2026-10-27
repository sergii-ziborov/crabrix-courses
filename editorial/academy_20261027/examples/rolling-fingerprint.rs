fn digit_hash(digits: &[u64]) -> u64 {
    let mut hash = 0;
    for &digit in digits { assert!(digit < 10); hash = (hash * 10 + digit) % 101; }
    hash // A fingerprint is not a collision-free identity.
}

fn main() {
    let result = digit_hash(&[3,1,4]).to_string();
    println!("{result}");
}
