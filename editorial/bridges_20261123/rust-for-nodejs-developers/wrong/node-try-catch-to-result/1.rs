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
    let factor = match unit {
        's' => 1,
        'm' => 60,
        'h' => 3600,
        _ => return Err(DurationError::BadFormat),
    };
    let n: u32 = digits.parse().map_err(|_| DurationError::BadFormat)?;
    let seconds = n.checked_mul(factor).ok_or(DurationError::TooLong)?;
    if seconds > 86_400 {
        return Err(DurationError::TooLong);
    }
    Ok(seconds)
}
