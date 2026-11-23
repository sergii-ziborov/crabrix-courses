// C original:
// /* 0 on success; -1 with errno = EINVAL or ERANGE on failure. */
// int parse_port(const char *text, uint16_t *out) {
//     char *end;
//     errno = 0;
//     long v = strtol(text, &end, 10);   /* also accepts spaces and a sign */
//     if (end == text || *end != '\0') { errno = EINVAL; return -1; }
//     if (errno == ERANGE || v < 1 || v > 65535) { errno = ERANGE; return -1; }
//     *out = (uint16_t)v;
//     return 0;
// }
#[derive(Debug, PartialEq)]
pub enum PortError {
    Empty,
    NotANumber,
    OutOfRange,
}

pub fn parse_port(text: &str) -> Result<u16, PortError> {
    todo!("implement the contract")
}
