pub fn truncate_at_boundary(text: &str, max_bytes: usize) -> &str {
    if text.len() <= max_bytes {
        return text;
    }
    let mut end = max_bytes;
    while !text.is_char_boundary(end) {
        end -= 1;
    }
    &text[..end]
}

pub fn initials(name: &str) -> String {
    name.split_whitespace()
        .filter_map(|word| word.chars().next())
        .map(|c| c.to_ascii_uppercase())
        .collect()
}
