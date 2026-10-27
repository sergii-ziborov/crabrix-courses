fn first_unique_ascii(text: &str) -> Option<char> {
    assert!(text.is_ascii());
    let mut count = [0; 256];
    for c in text.bytes() {
        count[c as usize] += 1;
    }
    text.bytes()
        .find(|&c| count[c as usize] == 1)
        .map(char::from)
}

fn main() {
    let result = first_unique_ascii("swiss").map_or("none".into(), |c| c.to_string());
    println!("{result}");
}
