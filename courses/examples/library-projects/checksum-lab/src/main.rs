fn fnv1a(bytes: &[u8]) -> u64 {
    let mut hash = 0xcbf2_9ce4_8422_2325_u64;
    for byte in bytes {
        hash ^= u64::from(*byte);
        hash = hash.wrapping_mul(0x100_0000_01b3);
    }
    hash
}

fn main() {
    for text in ["rust", "Rust", "rust!"] {
        println!("{text:<5} {:016x}", fnv1a(text.as_bytes()));
    }
}