#[derive(Debug, PartialEq)]
pub enum DurationError {
    BadFormat,
    TooLong,
}

pub fn parse_duration(text: &str) -> Result<u32, DurationError> {
    let (digits, unit) = match text.char_indices().last() {
        Some((index, unit)) => (&text[..index], unit),
        None => return Err(DurationError::BadFormat),
    };
    let factor: u64 = match unit {
        's' => 1,
        'm' => 60,
        'h' => 3600,
        _ => return Err(DurationError::BadFormat),
    };
    if digits.is_empty() || !digits.bytes().all(|b| b.is_ascii_digit()) {
        return Err(DurationError::BadFormat);
    }
    // Only ASCII digits remain, so a failed parse means the number is too large.
    let n: u64 = digits.parse().map_err(|_| DurationError::TooLong)?;
    let seconds = n.checked_mul(factor).ok_or(DurationError::TooLong)?;
    if seconds > 86_400 {
        return Err(DurationError::TooLong);
    }
    u32::try_from(seconds).map_err(|_| DurationError::TooLong)
}
