pub fn bar(percent: usize) -> String {
    let filled = percent / 10;
    format!("{}{}", "■".repeat(filled), "·".repeat(10 - filled))
}