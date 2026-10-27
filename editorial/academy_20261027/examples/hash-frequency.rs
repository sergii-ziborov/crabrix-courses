fn anagrams(a: &str, b: &str) -> bool {
    assert!(a.bytes().chain(b.bytes()).all(|c| c.is_ascii_lowercase()));
    let mut counts = [0_i32; 26];
    for c in a.bytes() {
        counts[(c - b'a') as usize] += 1;
    }
    for c in b.bytes() {
        counts[(c - b'a') as usize] -= 1;
    }
    counts.iter().all(|&n| n == 0)
}

fn main() {
    let result = anagrams("rust", "tsur").to_string();
    println!("{result}");
}
