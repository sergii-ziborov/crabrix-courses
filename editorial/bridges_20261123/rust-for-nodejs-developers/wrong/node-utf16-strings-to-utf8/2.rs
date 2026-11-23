pub fn initials(name: &str) -> String {
    name.split_whitespace()
        .map(|part| (part.as_bytes()[0] as char).to_ascii_uppercase())
        .collect()
}
