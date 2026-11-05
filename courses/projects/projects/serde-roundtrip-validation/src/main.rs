use serde::{Deserialize, Deserializer, Serialize, Serializer};
use serde::de::{Error, MapAccess, Visitor};
use serde::ser::SerializeStruct;
use std::fmt;

#[derive(Debug, PartialEq)]
struct Record { name: String, count: u32 }

// Explicit Serde traits keep this example portable to the released WASI
// compiler. They use the real serde/serde_json crates, without derive macros.
impl Serialize for Record {
    fn serialize<S: Serializer>(&self, s: S) -> Result<S::Ok, S::Error> {
        let mut fields = s.serialize_struct("Record", 2)?;
        fields.serialize_field("name", &self.name)?;
        fields.serialize_field("count", &self.count)?;
        fields.end()
    }
}
impl<'de> Deserialize<'de> for Record {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        struct RecordVisitor;
        impl<'de> Visitor<'de> for RecordVisitor {
            type Value = Record;
            fn expecting(&self, f: &mut fmt::Formatter) -> fmt::Result {
                f.write_str("a record with name and count")
            }
            fn visit_map<M: MapAccess<'de>>(self, mut map: M) -> Result<Record, M::Error> {
                let (mut name, mut count) = (None, None);
                while let Some(key) = map.next_key::<String>()? {
                    match key.as_str() {
                        "name" => {
                            if name.is_some() { return Err(M::Error::duplicate_field("name")); }
                            name = Some(map.next_value()?);
                        }
                        "count" => {
                            if count.is_some() { return Err(M::Error::duplicate_field("count")); }
                            count = Some(map.next_value()?);
                        }
                        _ => return Err(M::Error::unknown_field(&key, &["name", "count"])),
                    }
                }
                Ok(Record {
                    name: name.ok_or_else(|| M::Error::missing_field("name"))?,
                    count: count.ok_or_else(|| M::Error::missing_field("count"))?,
                })
            }
        }
        d.deserialize_struct("Record", &["name", "count"], RecordVisitor)
    }
}
fn decode(text: &str) -> Result<Record, Box<dyn std::error::Error>> {
    if text.len() > 4096 { return Err("record is too large".into()); }
    let row: Record = serde_json::from_str(text)?;
    if row.name.trim().is_empty() { return Err("blank name".into()); }
    Ok(row)
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let row = decode(r#"{"name":"crab 🦀","count":3}"#)?;
    let encoded = serde_json::to_string(&row)?;
    assert_eq!(decode(&encoded)?, row);
    for bad in [r#"{"name":" ","count":3}"#, r#"{"name":"crab"}"#,
        r#"{"name":"crab","count":-1}"#, r#"{"name":"crab","count":4294967296}"#,
        r#"{"name":"crab","count":3,"extra":true}"#,
        r#"{"name":"crab","name":"other","count":3}"#, "{"] {
        assert!(decode(bad).is_err());
    }
    assert!(decode(&"x".repeat(4097)).is_err());
    println!("Serde round-trip and validation: ok");
    Ok(())
}
