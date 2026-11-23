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
    match text.parse::<u16>() {
        Ok(0) | Err(_) => Err(PortError::OutOfRange), // only overflow is left
        Ok(port) => Ok(port),
    }
}
