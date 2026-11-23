#[derive(Debug, PartialEq)]
pub enum DurationError {
    BadFormat,
    TooLong,
}

pub fn parse_duration(text: &str) -> Result<u32, DurationError> {
    if text.is_empty() {
        return Err(DurationError::BadFormat);
    }
    let (digits, unit) = text.split_at(text.len() - 1);
    let factor: u64 = match unit {
        "s" => 1,
        "m" => 60,
        "h" => 3600,
        _ => return Err(DurationError::BadFormat),
    };
    if digits.is_empty() || !digits.bytes().all(|b| b.is_ascii_digit()) {
        return Err(DurationError::BadFormat);
    }
    let n: u64 = digits.parse().map_err(|_| DurationError::TooLong)?;
    let seconds = n.checked_mul(factor).ok_or(DurationError::TooLong)?;
    if seconds > 86_400 {
        return Err(DurationError::TooLong);
    }
    Ok(seconds as u32)
}
