pub fn label(name: &str, qty: u32, code: u32) -> String {
    format!("{name:8}|{qty:03}|{code:#06x}")
}
