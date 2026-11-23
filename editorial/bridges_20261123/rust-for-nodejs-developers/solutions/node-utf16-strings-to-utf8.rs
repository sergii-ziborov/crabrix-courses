pub fn initials(name: &str) -> String {
    name.split_whitespace()
        .filter_map(|part| part.chars().next())
        .flat_map(char::to_uppercase)
        .collect()
}
