fn replacement_length(text: &str, replacements: usize) -> usize {
    assert!(text.bytes().all(|c| c.is_ascii_uppercase()));
    let a = text.as_bytes();
    let mut counts = [0; 26];
    let (mut left, mut best) = (0, 0);
    for right in 0..a.len() {
        counts[(a[right] - b'A') as usize] += 1;
        while right + 1 - left - counts.iter().max().unwrap() > replacements {
            counts[(a[left] - b'A') as usize] -= 1;
            left += 1;
        }
        best = best.max(right + 1 - left);
    }
    best
}

fn main() {
    let result = replacement_length("AABABBA", 1).to_string();
    println!("{result}");
}
