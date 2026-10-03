fn main() {
    let ferris = [
        r"        _~^~^~_",
        r"    \) /  o o  \ (/",
        r"      '_   -   _'",
        r"      / '-----' \",
        r"     /  /     \  \",
        r"    /__/       \__\",
    ];

    println!("CRABRIX PIXEL LAB\n");
    ferris.iter().for_each(|line| println!("{line}"));
    println!("\n  fearless Rust, one line at a time");
}