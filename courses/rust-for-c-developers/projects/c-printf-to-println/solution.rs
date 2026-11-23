// C original:
// /* buf must hold the whole label, or snprintf silently truncates it. */
// void label(char *buf, size_t n, const char *name, unsigned qty, unsigned code) {
//     snprintf(buf, n, "%8s|%03u|%#06x", name, qty, code);
// }
pub fn label(name: &str, qty: u32, code: u32) -> String {
    todo!("implement the contract")
}
