pub fn clock(total_seconds: u32) -> String {
    format!("{}:{}", total_seconds / 60, total_seconds % 60)
}
