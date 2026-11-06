fn main() {
    for n in [0, 7, 42, u16::MAX] { assert_eq!(compat_api::label(n), format!("core={n}")); }
    #[cfg(feature = "details")]
    assert_eq!(compat_api::details(7), "core=7; details");
    #[cfg(feature = "trace")]
    assert_eq!(compat_api::trace(7), "trace: core=7");
    println!("core=7");
}
