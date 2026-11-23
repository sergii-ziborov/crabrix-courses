pub fn total_bytes(count: u32, size: u32) -> Option<u32> {
    Some(count * size)
}

pub fn to_byte(value: i32) -> Option<u8> {
    u8::try_from(value).ok()
}
