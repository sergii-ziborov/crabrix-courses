#[derive(Debug, PartialEq)]
pub enum DurationError {
    BadFormat,
    TooLong,
}

pub fn parse_duration(text: &str) -> Result<u32, DurationError> {
    let (digits, unit) = text.split_at(text.len() - 1);
    let factor = match unit {
        "s" => 1,
        "m" => 60,
        _ => 3600,
    };
    let n: u32 = digits.parse().unwrap();
    Ok(n * factor)
}
