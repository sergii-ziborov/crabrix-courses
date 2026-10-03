use std::fmt;

#[derive(Debug)]
enum ConfigError {
    Missing(String),
    NotANumber { key: String, value: String },
    OutOfRange { key: String, value: u32 },
}

impl fmt::Display for ConfigError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ConfigError::Missing(key) => write!(formatter, "missing key `{key}`"),
            ConfigError::NotANumber { key, value } => {
                write!(formatter, "`{key}` is not a number: {value}")
            }
            ConfigError::OutOfRange { key, value } => {
                write!(formatter, "`{key}` is out of range: {value}")
            }
        }
    }
}

fn lookup<'a>(source: &'a str, key: &str) -> Result<&'a str, ConfigError> {
    source
        .lines()
        .find_map(|line| line.split_once('='))
        .filter(|(name, _)| name.trim() == key)
        .map(|(_, value)| value.trim())
        .ok_or_else(|| ConfigError::Missing(key.to_string()))
}

fn port(source: &str) -> Result<u32, ConfigError> {
    let raw = lookup(source, "port")?;
    let value: u32 = raw.parse().map_err(|_| ConfigError::NotANumber {
        key: "port".to_string(),
        value: raw.to_string(),
    })?;
    if !(1..=65535).contains(&value) {
        return Err(ConfigError::OutOfRange { key: "port".to_string(), value });
    }
    Ok(value)
}

fn main() {
    for source in ["port = 8080", "port = eighty", "port = 99999", "host = local"] {
        match port(source) {
            Ok(value) => println!("{source:<16} -> ok: {value}"),
            Err(error) => println!("{source:<16} -> {error}"),
        }
    }
}