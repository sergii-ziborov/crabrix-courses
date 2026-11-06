pub fn label(id: u16) -> String { format!("core={id}") }
#[cfg(feature = "details")]
pub fn details(id: u16) -> String { format!("{}; details", label(id)) }
#[cfg(feature = "trace")]
pub fn trace(id: u16) -> String { format!("trace: {}", label(id)) }
pub fn requested() -> (bool, bool, bool) {
    (cfg!(feature = "pretty"), cfg!(feature = "details"), cfg!(feature = "trace"))
}
