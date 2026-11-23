#[derive(Debug, PartialEq)]
pub enum PortError {
    Empty,
    NotANumber,
    OutOfRange,
}

pub fn parse_port(text: &str) -> Result<u16, PortError> {
    if text.is_empty() {
        return Err(PortError::Empty);
    }
    if !text.bytes().all(|b| b.is_ascii_digit()) {
        return Err(PortError::NotANumber);
    }
    match text.parse::<u32>() {
        Ok(v) if (1..=65_535).contains(&v) => Ok(v as u16),
        Ok(_) => Err(PortError::OutOfRange),
        Err(_) => Err(PortError::NotANumber),
    }
}
