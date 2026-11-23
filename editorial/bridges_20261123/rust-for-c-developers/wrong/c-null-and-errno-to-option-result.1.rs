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
    match text.parse::<u16>() {
        Ok(0) => Err(PortError::OutOfRange),
        Ok(port) => Ok(port),
        Err(_) => Err(PortError::NotANumber),
    }
}
