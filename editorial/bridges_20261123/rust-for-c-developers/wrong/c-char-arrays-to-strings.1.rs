pub fn truncate_at_boundary(text: &str, max_bytes: usize) -> &str {
    &text[..max_bytes.min(text.len())]
}

pub fn initials(name: &str) -> String {
    name.split_whitespace()
        .filter_map(|word| word.chars().next())
        .flat_map(char::to_uppercase)
        .collect()
}
