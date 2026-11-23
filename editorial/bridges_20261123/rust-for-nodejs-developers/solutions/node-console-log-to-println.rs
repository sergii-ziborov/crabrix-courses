pub fn clock(total_seconds: u32) -> String {
    format!("{}:{:02}", total_seconds / 60, total_seconds % 60)
}
