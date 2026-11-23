pub fn after_prefix<'a>(line: &'a str, prefix: &str) -> Option<&'a str> {
    Some(&line[prefix.len()..])
}

pub fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() { a } else { b }
}
