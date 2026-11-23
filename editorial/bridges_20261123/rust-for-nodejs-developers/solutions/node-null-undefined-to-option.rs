pub struct Settings {
    pub page_size: Option<u32>,
    pub title: Option<String>,
}

pub fn page_size(s: Option<&Settings>) -> u32 {
    s.and_then(|s| s.page_size).unwrap_or(20)
}

pub fn title(s: Option<&Settings>) -> String {
    s.and_then(|s| s.title.clone()).unwrap_or_else(|| String::from("Untitled"))
}
