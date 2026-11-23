pub fn initials(name: &str) -> String {
    name.split_whitespace().map(|part| part[..1].to_uppercase()).collect()
}
