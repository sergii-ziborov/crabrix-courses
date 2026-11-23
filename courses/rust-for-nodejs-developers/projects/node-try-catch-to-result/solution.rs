// JavaScript original:
// function parseDuration(text) {            // "90s", "15m", "2h"
//   const match = /^(\d+)([smh])$/.exec(text);
//   if (!match) throw new Error("bad format");
//   const seconds = Number(match[1]) * { s: 1, m: 60, h: 3600 }[match[2]];
//   if (seconds > 86400) throw new Error("too long");
//   return seconds;
// }
#[derive(Debug, PartialEq)]
pub enum DurationError {
    BadFormat,
    TooLong,
}

pub fn parse_duration(text: &str) -> Result<u32, DurationError> {
    todo!("implement the contract")
}
