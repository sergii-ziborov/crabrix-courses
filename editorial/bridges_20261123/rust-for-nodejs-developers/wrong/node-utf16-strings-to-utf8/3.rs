pub fn initials(name: &str) -> String {
    name.split_whitespace()
        .filter_map(|part| part.chars().next())
        .map(|c| c.to_ascii_uppercase())
        .collect()
}
