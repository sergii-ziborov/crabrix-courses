// C original:
// /* Cuts s to at most max bytes. May split a multi-byte character in half. */
// void truncate_bytes(char *s, size_t max) { if (strlen(s) > max) s[max] = '\0'; }
// /* Writes the first byte of each word, passed through toupper(). */
// void initials(const char *name, char *out) {
//     int start = 1;
//     for (; *name; name++) {
//         if (isspace((unsigned char)*name)) { start = 1; continue; }
//         if (start) *out++ = (char)toupper((unsigned char)*name);
//         start = 0;
//     }
//     *out = '\0';
// }
pub fn truncate_at_boundary(text: &str, max_bytes: usize) -> &str {
    todo!("implement the contract")
}

pub fn initials(name: &str) -> String {
    todo!("implement the contract")
}
