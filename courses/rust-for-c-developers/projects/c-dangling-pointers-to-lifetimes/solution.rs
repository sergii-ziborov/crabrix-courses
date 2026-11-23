// C original:
// /* Points just past `prefix` inside `line`, or NULL. Never points into `prefix`. */
// const char *after_prefix(const char *line, const char *prefix) {
//     size_t n = strlen(prefix);
//     return strncmp(line, prefix, n) == 0 ? line + n : NULL;
// }
// const char *longer(const char *a, const char *b) { return strlen(a) >= strlen(b) ? a : b; }
pub fn after_prefix<'a>(line: &'a str, prefix: &str) -> Option<&'a str> {
    todo!("implement the contract")
}

pub fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    todo!("implement the contract")
}
