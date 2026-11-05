"""Practical teaching paths. Native-only Cargo examples are explicitly labelled."""


def add_routes(unit, lesson, lab):
    unit("projects", "files-data", "Files & Data", "Read, validate, transform, and save a small data report")
    lesson("projects", "files-data", "buffered-line-input", "Buffered Line Input", "BufRead, Cursor, and fallible iteration",
        "Separate a streaming parser from the place its bytes come from.",
        "A reader can fail between records; handle both I/O and parse errors.", [
        "A file is a source of bytes, not a ready-made collection of valid records. Give the parser a generic `R: BufRead` input so the same function can accept a buffered file, locked stdin, or an in-memory `Cursor`. This separates the data transformation from permissions, paths, and device-specific I/O. It also makes the parser easy to exercise without creating a real file.",
        "The `lines()` iterator yields `io::Result<String>` values. First handle the read result, then decide what a line means. For this small report, trim whitespace, skip blank lines, and parse every other line as `i64`. A malformed nonblank line is an error, not a zero and not a reason to silently discard the record. Include the one-based physical line number in that error, even when earlier lines were blank.",
        "Use `checked_add` when the accepted numeric domain can overflow the accumulator. Returning a clear error preserves the contract instead of making behavior depend on a debug or release overflow setting. Streaming avoids retaining every record, but one unusually long line can still allocate a large string. A production parser needs a separate record-size limit; buffering alone is not a memory quota.",
        "Local compiler profile: standard library only. The lab uses `Cursor` and needs no filesystem permission, package download, network request, or backend execution. Once the parser is correct, a desktop adapter can pass `BufReader::new(File::open(path)?)`. In Crabrix, an adapter must use files granted to its sandbox. Keep the transformation independently testable before adding that adapter."
        ], 'use std::io::{BufRead, Cursor};\nfn main() {\n    let input = Cursor::new("12\\n\\n8\\n");\n    for line in input.lines() {\n        println!("{}", line.unwrap());\n    }\n}',
        "Sum nonblank integer records and report the physical line of the first invalid record.",
        "Why can filter_map(Result::ok) silently corrupt this report?",
        ["It turns every successful line into bytes", "It drops read failures instead of reporting incomplete input", "It forces all numbers to zero"], 1,
        "Dropping errors can produce a believable total from only part of the input. Propagate read failures and identify malformed records.",
        "A buffered reader has already validated every record.", "Buffering changes how bytes are read; parsing and error policy are separate.",
        [("Read", "Unwrap each fallible line before parsing its contents."), ("Validate", "Track the physical line number and reject invalid integers."), ("Accumulate", "Add with overflow detection and return one result.")],
        "Replace Cursor with a deliberately failing Read implementation. Confirm the report returns an error rather than a partial total.")
    lab("projects", "buffered-line-input", "pub fn total<R: std::io::BufRead>(reader: R) -> Result<i64, String>",
        '    let mut sum = 0i64;\n    for (index, line) in reader.lines().enumerate() {\n        let line = line.map_err(|_| "read failed".to_owned())?;\n        if line.trim().is_empty() { continue; }\n        let n: i64 = line.trim().parse().map_err(|_| format!("line {}", index + 1))?;\n        sum = sum.checked_add(n).ok_or_else(|| "overflow".to_owned())?;\n    }\n    Ok(sum)',
        [('solution::total(std::io::Cursor::new("12\\n\\n8\\n"))', 'Ok(20)'), ('solution::total(std::io::Cursor::new(""))', 'Ok(0)'), ('solution::total(std::io::Cursor::new("\\nnope"))', 'Err("line 2".to_owned())'), ('solution::total(std::io::Cursor::new("9223372036854775807\\n1"))', 'Err("overflow".to_owned())'), ('solution::total(std::io::Cursor::new("-4\\r\\n 2 "))', 'Ok(-2)')],
        "Implement total(reader): skip blank lines, sum trimmed i64 records with checked_add, return line N for the first malformed physical line, overflow for arithmetic overflow, and read failed for an I/O failure.", mutant="Ok(0)",
        preamble='struct Broken;\nimpl std::io::Read for Broken {\n    fn read(&mut self, _: &mut [u8]) -> std::io::Result<usize> { Err(std::io::Error::other("broken")) }\n}',
        extra='    assert_eq!(solution::total(std::io::BufReader::new(Broken)), Err("read failed".to_owned()));')

    lesson("projects", "files-data", "paths-and-boundaries", "Paths & Boundaries", "Path, PathBuf, and lexical validation",
        "Treat a path as structured input and keep lexical checks distinct from filesystem authority.",
        "Joining a path is not permission checking, and lexical validation does not resolve symlinks.", [
        "Use `Path` for a borrowed path and `PathBuf` for an owned path that can be extended. Concatenating strings can mishandle separators and makes it difficult to see which input controls the destination. `root.join(name)` expresses the relationship, but it does not guarantee that the result stays beneath root. In particular, an absolute name can replace the beginning, and parent components can walk upward.",
        "For the lab, accept only a nonempty sequence of normal relative components. Reject an absolute path, any parent component, and a path containing only current-directory components. Joining the accepted components gives a useful lexical rule for an imported project name. Spaces and Unicode are legitimate filename content; do not reject them merely because a shell command would need quoting. No shell command is involved in this operation.",
        "This is deliberately not a complete security boundary for a hostile filesystem. A symlink inside root may point elsewhere, and checking a canonical path before opening it can race with a later replacement. Real authority comes from the host's granted directory handles and platform-specific safe open operations. A WebAssembly guest should not gain access to a user's home directory just because a path string looks harmless.",
        "Local compiler profile: standard library only. The exercise manipulates paths without touching disk. The following file lesson demonstrates a granted sandbox destination. Keep these layers separate: parse a requested relative path, apply the host's access policy, and handle the actual open result. This separation is useful when importing archives or moving project files as well as when writing a command-line report."
        ], 'use std::path::Path;\nfn main() {\n    let path = Path::new("reports").join("daily.txt");\n    assert_eq!(path.file_name().unwrap(), "daily.txt");\n}',
        "Validate a relative destination before joining it to a trusted root.",
        "Does rejecting .. components prevent escape through a symlink?",
        ["Yes, every filesystem must interpret it lexically", "Yes, when the name ends in .txt", "No; symlink resolution and authority require separate protection"], 2,
        "The lexical rule rejects obvious traversal but does not establish authority over a changing filesystem.",
        "A root.join call always stays inside root.", "An absolute argument or parent traversal changes the destination; symlinks add another layer.",
        [("Inspect", "Split the requested path into components."), ("Reject", "Refuse roots, prefixes, parents, and an empty effective name."), ("Join", "Append accepted normal components; leave permissions to the host.")],
        "Explain which additional host guarantees are needed before using this validator to extract an untrusted archive.")
    lab("projects", "paths-and-boundaries", "pub fn destination(root: &std::path::Path, name: &std::path::Path) -> Option<std::path::PathBuf>",
        '    let mut relative = std::path::PathBuf::new();\n    for component in name.components() {\n        match component {\n            std::path::Component::Normal(part) => relative.push(part),\n            std::path::Component::CurDir => {},\n            _ => return None,\n        }\n    }\n    if relative.as_os_str().is_empty() { None } else { Some(root.join(relative)) }',
        [('solution::destination(std::path::Path::new("root"), std::path::Path::new("reports/day.txt"))', 'Some(std::path::PathBuf::from("root/reports/day.txt"))'), ('solution::destination(std::path::Path::new("root"), std::path::Path::new("../x"))', 'None'), ('solution::destination(std::path::Path::new("root"), std::path::Path::new("/x"))', 'None'), ('solution::destination(std::path::Path::new("root"), std::path::Path::new("."))', 'None'), ('solution::destination(std::path::Path::new("root"), std::path::Path::new("./résumé.txt"))', 'Some(std::path::PathBuf::from("root/résumé.txt"))')],
        "Accept normal relative components and optional dot components, reject parent/root/prefix components and an empty effective name, then join the trusted root. This is lexical validation, not a symlink security boundary.", mutant="None")

    lesson("projects", "files-data", "sandbox-file-roundtrip", "Save & Read a Text File", "Fallible filesystem effects in a granted directory",
        "Make the file effect explicit, return errors, and verify the bytes that came back.",
        "A successful write is not a promise of crash-safe durability.", [
        "A small report can keep parsing pure and put file access in a narrow adapter. Accept a borrowed `Path`, write UTF-8 text, read it back, and return `io::Result<String>`. The question mark propagates the real I/O error to the caller. An unreadable destination, missing parent directory, or invalid UTF-8 on a later read is not equivalent to an empty report.",
        "Local compiler profile: standard library with Crabrix's writable `/sandbox` directory. That is a guest path granted by the runtime, not arbitrary access to the iPhone's Files library. The verification harness chooses a sandbox path on wasm32 and a temporary working-directory path for the desktop test. It checks empty text, multiline text, Unicode, and replacement of an existing file. The lesson does not request network or account access.",
        "`fs::write` creates or truncates the target. That is appropriate for this exercise's replace-the-report contract, but it can destroy an older report before a new write finishes. A crash-safe save strategy typically writes a sibling temporary file, flushes and syncs as required, then replaces the destination. Atomic rename and durability details depend on the host filesystem; do not advertise a portable power-loss guarantee from a single write call.",
        "Round-trip equality proves the observed contents for this run. It does not prove every possible failure mode or make concurrent writers safe. If two participants edit a shared Playground, coordinate document updates before asking either participant to save a local copy. A remote output event must never silently trigger the filesystem effect on another device. Keep execution and saving explicit actions owned by the local user."
        ], 'use std::{fs, io};\nfn main() -> io::Result<()> {\n    // Crabrix guest path; choose a local path for desktop Cargo.\n    fs::write("/sandbox/report.txt", "crab: 3\\n")?;\n    let text = fs::read_to_string("/sandbox/report.txt")?;\n    assert_eq!(text, "crab: 3\\n");\n    Ok(())\n}',
        "Write the supplied UTF-8 text and return its exact read-back contents.",
        "What does fs::write do to an existing target?",
        ["It appends automatically", "It creates or truncates the file", "It guarantees a power-loss-safe transaction"], 1,
        "The target is created or truncated. Crash-safe replacement and durability are separate design requirements.",
        "Writing a file automatically makes the save transactional.", "Creation/truncation, atomic replacement, and durable persistence are distinct guarantees.",
        [("Choose authority", "Use only a destination granted by the local runtime."), ("Perform effect", "Propagate write and read errors with question marks."), ("Verify", "Compare exact text, including empty input and Unicode.")],
        "Design a temporary-file replacement sequence for desktop Cargo and list what could fail at each step.")
    p='std::path::Path::new(if cfg!(target_arch = "wasm32") { "/sandbox/crabrix-report.txt" } else { "crabrix-report.txt" })'
    lab("projects", "sandbox-file-roundtrip", "pub fn save_report(path: &std::path::Path, text: &str) -> std::io::Result<String>",
        '    std::fs::write(path, text)?;\n    std::fs::read_to_string(path)',
        [(f'solution::save_report({p}, "crab: 3\\n").unwrap()', '"crab: 3\\n"'), (f'solution::save_report({p}, "").unwrap()', '""'), (f'solution::save_report({p}, "Rust 🦀\\nnext").unwrap()', '"Rust 🦀\\nnext"')],
        "Use fs::write and fs::read_to_string, propagating errors. Return the exact saved text; do not append to an existing file.", mutant='Ok(String::new())')

    lesson("projects", "files-data", "validated-records", "Validate Data Records", "A bounded text format with precise errors",
        "Specify a small input format before implementing its parser.",
        "Malformed records must not disappear from a successful report.", [
        "The report format in this exercise is intentionally smaller than CSV: one nonblank record per line, exactly two comma-separated fields, a nonempty trimmed name, and an unsigned count. Quoting and escaped commas are unsupported and must be rejected. Calling a split-on-comma parser a complete CSV parser would be misleading; real CSV permits quoted delimiters, embedded newlines, and escaped quote characters.",
        "Parse the entire record before changing the report total. Validate the number of fields, trim both fields, check that the name is nonempty, and parse the count as `u32`. Report a typed or clearly documented error instead of substituting zero. At an application boundary, attach a one-based line number while preserving enough information to explain whether the structure or the number was invalid.",
        "The compiler lab focuses on one record so its contract stays small. A later adapter can reuse the buffered-line reader, skip blank lines, and call this parser. A successful parse returns owned data that can outlive the input buffer. If ownership costs become significant, consider a borrowed intermediate representation, but measure before introducing lifetimes into every public API.",
        "Local compiler profile: standard library only. Tests cover whitespace, zero, extra fields, missing fields, a negative count, overflow, and unsupported quotes. These cases are examples of a broader rule: input validation is a part of the data model, not a cosmetic step at the end. Before extending this format, decide whether an established CSV crate is a better fit than adding another exception to a home-grown grammar."
        ], 'fn main() {\n    let fields: Vec<_> = "crab, 3".split(\',\').map(str::trim).collect();\n    assert_eq!(fields, ["crab", "3"]);\n    // Validate field count, name, and count before accepting a record.\n}',
        "Parse one bounded name,count record without claiming full CSV support.",
        "Why is split(',') insufficient for general CSV?",
        ["CSV can contain delimiters inside quoted fields", "CSV never contains commas", "Rust strings cannot contain newlines"], 0,
        "Quoted fields change the grammar. Use a CSV parser for the general format; keep this exercise's restrictions explicit.",
        "Every comma-delimited file can be safely parsed with split.", "A simplified grammar is useful only when its accepted and rejected inputs are explicit.",
        [("Shape", "Require exactly two fields and refuse quote characters."), ("Domain", "Require a name and a valid unsigned count."), ("Own", "Return an owned name so the record can outlive its input buffer.")],
        "Add line-number context in a streaming adapter without turning errors into skipped records.")
    lab("projects", "validated-records", "pub fn record(text: &str) -> Result<(String, u32), String>",
        '    if text.contains(\'"\') { return Err("invalid".to_owned()); }\n    let fields: Vec<_> = text.split(\',\').map(str::trim).collect();\n    if fields.len() != 2 || fields[0].is_empty() { return Err("invalid".to_owned()); }\n    let count = fields[1].parse::<u32>().map_err(|_| "invalid".to_owned())?;\n    Ok((fields[0].to_owned(), count))',
        [('solution::record(" crab , 3 ")', 'Ok(("crab".to_owned(), 3))'), ('solution::record("rust,0")', 'Ok(("rust".to_owned(), 0))'), ('solution::record(",2")', 'Err("invalid".to_owned())'), ('solution::record("a,2,x")', 'Err("invalid".to_owned())'), ('solution::record("a,-1")', 'Err("invalid".to_owned())'), ('solution::record("a,4294967296")', 'Err("invalid".to_owned())'), ('solution::record("\\\"a\\\",2")', 'Err("invalid".to_owned())')],
        "Return a trimmed owned name and u32 count from exactly two comma-separated fields. Reject quotes, empty names, extra/missing fields, invalid counts and overflow with Err(invalid). This is not a general CSV parser.", mutant='Err("invalid".to_owned())')

    lesson("projects", "files-data", "serde-roundtrip-validation", "Serde: Decode, Validate, Encode", "Serialization is not domain validation",
        "Turn JSON into a transport type, validate it, and only then create a domain value.",
        "Deserialization checks the transport shape; your domain invariants still need an explicit boundary.", [
        "JSON describes data exchange, while your application model describes valid state. Deserialize into a small transport structure, then convert it into a domain value whose constructor enforces the rules. A syntactically valid JSON object can still contain a blank display name, a negative quantity, or a count larger than the application supports. Do not spread those checks across every consumer.",
        "Desktop Cargo profile: this example needs `serde` with its `derive` feature and `serde_json`. The derive implementation is a procedural macro; it is not supplied by the standard library. Put `serde = { version = \"1\", features = [\"derive\"] }` and `serde_json = \"1\"` in dependencies, retain Cargo.lock, and run the example with Cargo. In Crabrix, check the prepared package and procedural-macro compatibility report before expecting the same project to build. This reading deliberately does not mark that external toolchain path as a standard-library compiler lab.",
        "Choose an evolution policy. By default, unknown struct fields are ignored; `deny_unknown_fields` rejects them. Neither choice is universally safer: rejecting surprises is useful for a tightly controlled command, while forward-compatible clients may need to tolerate new fields. Document the decision, and use an explicit format version when a later change would reinterpret an existing field.",
        "Compare decoded meaning in a round-trip test rather than relying on object-key order or pretty-print whitespace. Avoid printing full input documents into error logs when they may contain private data. Limit input size before decoding untrusted text, and distinguish a parse error from a domain validation error. The lab in the previous lesson stays dependency-free; this lesson shows how to replace its intentionally restricted transport format with an established serialization library."
        ], 'use serde::{Deserialize, Serialize};\n#[derive(Debug, PartialEq, Serialize, Deserialize)]\n#[serde(deny_unknown_fields)]\nstruct Record { name: String, count: u32 }\nfn main() -> Result<(), Box<dyn std::error::Error>> {\n    let row: Record = serde_json::from_str(r#"{"name":"crab","count":3}"#)?;\n    if row.name.trim().is_empty() { return Err("blank name".into()); }\n    let encoded = serde_json::to_string(&row)?;\n    assert_eq!(serde_json::from_str::<Record>(&encoded)?, row);\n    Ok(())\n}',
        "On desktop Cargo, run the example with the two declared dependencies. Add a domain constructor, then test blank names, missing fields, unknown fields, and an out-of-range count.",
        "Does deriving Deserialize guarantee that name is nonblank?",
        ["Yes, all String fields are nonblank", "No, the application must validate that invariant", "Only if JSON keys are sorted"], 1,
        "A String is structurally valid even when empty. Validate domain invariants after decoding.",
        "Valid JSON is already a valid business record.", "The format and type checker do not know application-specific constraints.",
        [("Decode", "Turn JSON into a transport structure and preserve a useful error."), ("Validate", "Construct domain state only after checking its invariants."), ("Encode", "Round-trip meaning and document the schema's evolution policy.")],
        "Design a versioned settings format that accepts an older document without silently changing the meaning of a stored field.", 20)

    add_api(unit, lesson, lab)
    add_testing(unit, lesson, lab)
    add_async(unit, lesson)
    add_wasm(unit, lesson, lab)


def add_api(unit, lesson, lab):
    unit("ownership", "api-boundaries", "API Boundaries", "Parse once, borrow flexibly, and preserve error meaning")
    lesson("ownership", "api-boundaries", "fromstr-domain-values", "FromStr & Domain Values", "A validated constructor behind a parsing trait",
        "Convert raw text into a value that cannot represent an invalid port.",
        "A conversion is useful when its output establishes an invariant, not just a new spelling.", [
        "A network port number fits in a u16, but this application's user-selectable port must also be nonzero. A private field and a checked constructor prevent callers from manufacturing an invalid value through ordinary safe code. `FromStr` then makes the text boundary idiomatic: callers write `text.parse::<Port>()` and handle the declared error. The conversion is fallible because not every string belongs to the domain.",
        "Keep syntax and domain failures distinct when the caller can act on that difference. In the lab, malformed text and numeric overflow produce `invalid`; the valid integer zero produces `zero`. The parser trims surrounding whitespace, but it does not invent a default when the input is absent. Decide separately whether a command-line flag, a configuration file, or a form field is allowed to omit the value.",
        "A `From<T>` implementation promises an infallible conversion, so do not implement it by panicking for an ordinary invalid input. Use `TryFrom` for a fallible typed conversion and `FromStr` for parsing borrowed text. These traits can delegate to the same checked constructor, avoiding divergent rules between your JSON adapter and your command-line adapter. A constructor should not secretly open a socket merely because it validates a port number.",
        "Local compiler profile: standard library only. The typed lab checks zero, whitespace, the largest valid u16, negative text, and overflow. The reading demonstrates the trait implementation; the lab focuses on the checked parsing boundary so its observable contract is straightforward. As an extension, wrap the result in a private-field Port and make every public creation path use the same invariant."
        ], 'use std::str::FromStr;\n#[derive(Debug, PartialEq)]\nstruct Port(u16);\nimpl FromStr for Port {\n    type Err = &\'static str;\n    fn from_str(text: &str) -> Result<Self, Self::Err> {\n        let n = text.trim().parse::<u16>().map_err(|_| "invalid")?;\n        if n == 0 { Err("zero") } else { Ok(Port(n)) }\n    }\n}\nfn main() { assert_eq!(" 8080 ".parse(), Ok(Port(8080))); }',
        "Build a checked port parser with an explicit error policy.",
        "Which trait fits a typed conversion that may reject a value?",
        ["From, with a panic on invalid values", "Copy, because parsing copies bytes", "TryFrom, with an error result"], 2,
        "TryFrom communicates a fallible conversion in its type. FromStr is the corresponding idiom for parsing text.",
        "A conversion trait should silently choose a default on bad input.", "A fallible boundary returns enough information for the caller to choose a policy.",
        [("Parse", "Trim and parse u16 without discarding errors."), ("Validate", "Reject zero as a separate domain violation."), ("Encapsulate", "Prevent unchecked construction of the domain value.")],
        "Implement TryFrom<u16> for Port and have FromStr delegate to it. Verify that both paths reject zero.")
    lab("ownership", "fromstr-domain-values", "pub fn parse_port(text: &str) -> Result<u16, &'static str>",
        '    let n = text.trim().parse::<u16>().map_err(|_| "invalid")?;\n    if n == 0 { Err("zero") } else { Ok(n) }',
        [('solution::parse_port(" 8080 ")', 'Ok(8080)'), ('solution::parse_port("0")', 'Err("zero")'), ('solution::parse_port("65535")', 'Ok(65535)'), ('solution::parse_port("65536")', 'Err("invalid")'), ('solution::parse_port("-1")', 'Err("invalid")'), ('solution::parse_port("abc")', 'Err("invalid")')],
        "Trim and parse a u16 port. Return zero for the zero-domain error and invalid for malformed or overflowing text; otherwise return the nonzero value.", mutant="Ok(8080)")

    lesson("ownership", "api-boundaries", "option-result-transpose", "Compose Optional Fallible Input", "map, transpose, and explicit defaults",
        "Keep missing configuration distinct from a configuration that is present but invalid.",
        "Apply defaults to absence, not to every failure.", [
        "An optional configuration value can have three outcomes: no value was supplied, a valid value was supplied, or an invalid value was supplied. `Result<Option<T>, E>` preserves those outcomes. Converting an error into None with `ok()` loses the distinction, and adding `unwrap_or` too early can make a typo look like a deliberate default.",
        "Map a parser over `Option<&str>` and the intermediate type becomes `Option<Result<T, E>>`. `transpose()` changes that nesting into `Result<Option<T>, E>`. It does not run the parser for None, hide an error, or pick a default. A match expression can implement the same behavior and may be easier while learning; combinators are useful when they keep the boundary readable.",
        "The exercise accepts an optional nonzero u16 port. None stays Ok(None). Some text is trimmed, parsed, and validated using the same policy as the previous lesson. Some empty text is an invalid supplied value, not absence. That distinction matters for environment variables, web forms, and configuration merging, where an explicit invalid override should not silently fall back to an older value.",
        "Local compiler profile: standard library only. Verify absent input, valid text, blank text, zero, and overflow separately. After the conversion succeeds, the application can deliberately choose `port.unwrap_or(default_port)`. Keep that policy outside the parser so another caller can require a value instead. Error-preserving composition is more important than making a chain of adapters as short as possible."
        ], 'fn main() {\n    let input = Some("42");\n    let parsed: Result<Option<u16>, _> = input.map(str::parse::<u16>).transpose();\n    assert_eq!(parsed, Ok(Some(42)));\n    let absent: Option<&str> = None;\n    assert_eq!(absent.map(str::parse::<u16>).transpose(), Ok(None));\n}',
        "Compose a checked parser with optional input without erasing errors.",
        "What is the type after transposing Option<Result<u16, E>>?",
        ["Result<Option<u16>, E>", "Option<u16>, with every error removed", "Result<u16, Option<E>>"], 0,
        "Transpose preserves absence and errors while moving Result to the outside.",
        "An invalid supplied value should always become the default.", "A default is a policy for absence; invalid input often needs to be reported.",
        [("Absent", "None does not invoke the parser."), ("Present", "Some text invokes the same checked parser as required input."), ("Compose", "Transpose preserves the error and lets the caller choose a default later.")],
        "Implement the same function with match and with map/transpose; compare behavior on blank text and absent input.")
    lab("ownership", "option-result-transpose", "pub fn optional_port(text: Option<&str>) -> Result<Option<u16>, &'static str>",
        '    text.map(|value| {\n        let n = value.trim().parse::<u16>().map_err(|_| "invalid")?;\n        if n == 0 { Err("zero") } else { Ok(n) }\n    }).transpose()',
        [('solution::optional_port(Some(" 80 "))', 'Ok(Some(80))'), ('solution::optional_port(None)', 'Ok(None)'), ('solution::optional_port(Some(""))', 'Err("invalid")'), ('solution::optional_port(Some("0"))', 'Err("zero")'), ('solution::optional_port(Some("65536"))', 'Err("invalid")')],
        "Preserve None as Ok(None). For supplied text use the preceding port policy: zero is a zero error, bad syntax/overflow is invalid, and nonzero u16 becomes Ok(Some(n)).", mutant="Ok(None)")

    lesson("ownership", "api-boundaries", "asref-borrowed-inputs", "Flexible Borrowed Inputs", "AsRef without unnecessary ownership",
        "Accept several string-like types when the operation only needs a borrowed view.",
        "Ask for ownership only when the operation needs to keep or consume the value.", [
        "A function that only inspects text does not need a String allocation from every caller. A borrowed `&str` is often the simplest signature. `AsRef<str>` is useful when an API intentionally accepts several owned or borrowed string-like types and immediately obtains a string slice from them. It is a cheap reference conversion, not a general parsing or validation mechanism.",
        "The example accepts a generic input, calls `as_ref()`, trims surrounding whitespace, and returns the number of Unicode scalar values. It never stores a reference after the call returns. Taking T by value still moves an owned String passed directly; callers that want to keep it can pass a reference. Generic syntax does not repeal ownership rules.",
        "Choose the narrowest useful contract. A public function taking `&str` is easy to read and accepts `&String` through coercion. An `AsRef<Path>` parameter can be convenient for a file adapter, but path conversion does not grant filesystem permission. Similarly, `AsRef<str>` does not prove a string is a valid URL, port, or record. Keep the validated domain constructor from the earlier lesson as a separate operation.",
        "Local compiler profile: standard library only. The lab calls the same function with a string literal, a String, and a borrowed String. It includes accented text and an emoji so byte length cannot accidentally pass as character count. Rust chars are Unicode scalar values; they are not the same as user-perceived grapheme clusters, so describe the result precisely rather than calling it a universal display width."
        ], 'fn scalar_count(text: impl AsRef<str>) -> usize {\n    text.as_ref().trim().chars().count()\n}\nfn main() {\n    let owned = String::from(" É🦀 ");\n    assert_eq!(scalar_count(&owned), 2);\n    assert_eq!(owned, " É🦀 ");\n}',
        "Accept string-like inputs and count trimmed Unicode scalar values.",
        "If an owned String is passed by value to fn f<T: AsRef<str>>(value: T), is the original still available?",
        ["Always, because AsRef implies Copy", "No, unless it was borrowed or cloned before the call", "Only when the text is ASCII"], 1,
        "AsRef supplies a borrowed view inside the function. Passing the owned argument by value still moves it.",
        "AsRef means arguments can never be moved.", "The conversion is borrowed, but the parameter's ownership mode still matters.",
        [("Accept", "Choose a borrowed slice or a justified generic input."), ("View", "Call as_ref only for the lifetime of the operation."), ("Specify", "Count scalar values, not bytes or grapheme clusters.")],
        "Compare a &str API and an impl AsRef<str> API at three call sites. Keep the simpler public contract unless flexibility has a concrete benefit.")
    lab("ownership", "asref-borrowed-inputs", "pub fn scalar_count<T: AsRef<str>>(text: T) -> usize",
        '    text.as_ref().trim().chars().count()',
        [('solution::scalar_count(" crab ")', '4'), ('solution::scalar_count(String::from(""))', '0'), ('solution::scalar_count(&String::from(" É🦀 "))', '2'), ('solution::scalar_count("e\\u{301}")', '2')],
        "Trim surrounding whitespace and count Unicode scalar values for any AsRef<str> input. This is not byte length or grapheme count.", mutant="0")


def add_testing(unit, lesson, lab):
    unit("projects", "reliability-labs", "Reliability Labs", "Properties, hostile input, and regression cases")
    lesson("projects", "reliability-labs", "properties-and-oracles", "Test Properties, Not Just Examples", "An independent oracle and bounded generated cases",
        "A normalization function should satisfy laws on many inputs, not only one expected output.",
        "Use an independent oracle; repeating the implementation in the assertion repeats its bugs.", [
        "A few examples help explain a function, while properties describe behavior across a family of inputs. For a canonical set of integer IDs, the output must be sorted, contain no duplicates, preserve membership, and be idempotent. None of those laws alone is enough: a function returning an empty vector is sorted and idempotent but discards every ID.",
        "Compare against an independent model such as BTreeSet rather than copying the same sort-and-deduplicate sequence into the test. Generate bounded combinations from a small domain, including negative values and repeated IDs. Small exhaustive spaces are often excellent at finding boundary mistakes, are deterministic, and require no external dependency. They still establish evidence only for the inputs tested, not a proof for every vector length.",
        "The compiler lab's private harness checks concrete outputs and generated membership behavior. A learner cannot make it pass merely by editing an assertion in the starter. The code under test remains editable; the verdict is produced by a separate harness after calls finish. Treat this as feedback about the exercise contract, not a hostile-code containment guarantee: arbitrary source remains inside the ordinary bounded local runtime.",
        "Local compiler profile: standard library only. On desktop Cargo, property-testing crates such as proptest can generate larger spaces and shrink a failing input into a small counterexample. Preserve the smallest failure as a named regression test even after the generator finds it. Do not call a deterministic loop a fuzzing campaign or claim complete correctness because a finite test suite passed."
        ], 'fn canonical(mut ids: Vec<i32>) -> Vec<i32> {\n    ids.sort_unstable();\n    ids.dedup();\n    ids\n}\nfn main() {\n    let once = canonical(vec![3, 1, 3]);\n    assert_eq!(once, [1, 3]);\n    assert_eq!(canonical(once.clone()), once);\n}',
        "Normalize IDs while preserving the complete set of values.",
        "Which property rules out a function that always returns an empty vector?",
        ["Idempotence alone", "Sorted output alone", "Preserving input membership"], 2,
        "Membership preservation catches lost data. Combine it with ordering and uniqueness rather than trusting a single weak property.",
        "A single algebraic property proves the whole implementation.", "Several incorrect functions satisfy one convenient property; use a complete contract and independent model.",
        [("State laws", "Specify order, uniqueness, membership, and idempotence."), ("Generate", "Enumerate a bounded input space reproducibly."), ("Compare", "Use a different data structure as the oracle.")],
        "Write a desktop proptest version and keep one shrunk failure as a deterministic regression test.")
    lab("projects", "properties-and-oracles", "pub fn canonical(mut ids: Vec<i32>) -> Vec<i32>",
        '    ids.sort_unstable();\n    ids.dedup();\n    ids',
        [('solution::canonical(vec![3, 1, 3])', 'vec![1, 3]'), ('solution::canonical(vec![])', 'vec![]'), ('solution::canonical(vec![-2, 0, -2, 4])', 'vec![-2, 0, 4]'), ('solution::canonical(vec![5, 5, 5])', 'vec![5]'), ('solution::canonical(vec![i32::MAX, i32::MIN, 0])', 'vec![i32::MIN, 0, i32::MAX]')],
        "Return all distinct input IDs in ascending order. Preserve negative values and integer extremes; empty input stays empty.", mutant="vec![]",
        extra='''    for a in -2..=2 { for b in -2..=2 { for c in -2..=2 {
        let input = vec![a, b, c, a];
        let oracle: Vec<_> = input.iter().copied().collect::<std::collections::BTreeSet<_>>().into_iter().collect();
        let actual = solution::canonical(input);
        assert_eq!(actual, oracle);
        assert_eq!(solution::canonical(actual.clone()), actual);
    } } }''')

    lesson("projects", "reliability-labs", "hostile-parser-inputs", "Adversarial Parser Tests", "Reject malformed data without panic or silent truncation",
        "Start with a grammar, then make a test table for the ways input can violate it.",
        "No panic is necessary for an expected invalid input, but success must still mean the whole record was accepted.", [
        "A parser that never panics can still be wrong if it silently ignores a suffix, rounds an overflowing value, or accepts a missing field. Write down the accepted grammar before writing adversarial cases. This lesson's grammar is exactly two trimmed unsigned decimal byte values separated by one colon. Both values must fit u8. A third field, an empty field, a sign, or nondecimal text is invalid.",
        "Organize tests by failure class instead of adding random strings without a hypothesis. Test a missing delimiter, repeated delimiters, a negative value, a leading plus, overflow, whitespace-only fields, Unicode digits, and the two valid numeric boundaries. Rust's numeric parser may accept syntax you did not intend, so enforce the grammar's ASCII-digit rule before parsing. Return None for this small API; a richer user-facing parser should expose a precise error type.",
        "Avoid `filter_map` on fallible fields: it can turn a three-field record with one bad field into two apparently good values. Do not index a collected vector until its length has been checked. Check complete consumption so a valid prefix cannot conceal trailing junk. These ideas transfer directly to command input, imported project metadata, and network messages.",
        "Local compiler profile: standard library only. The lab uses deterministic hostile cases. Desktop cargo-fuzz is a separate toolchain that can explore byte inputs and save crashes; it does not belong to the browser or iOS run profile merely because the parser itself is portable. A useful fuzz target asserts domain properties after successful parsing and never treats rejection of arbitrary bytes as a bug."
        ], 'fn decimal_byte(text: &str) -> Option<u8> {\n    let text = text.trim();\n    if text.is_empty() || !text.bytes().all(|b| b.is_ascii_digit()) { return None; }\n    text.parse().ok()\n}\nfn main() {\n    assert_eq!(decimal_byte("255"), Some(255));\n    assert_eq!(decimal_byte("256"), None);\n    assert_eq!(decimal_byte("+1"), None);\n}',
        "Implement the complete two-byte grammar and reject every malformed record.",
        "Why test a leading plus sign separately from a negative number?",
        ["The declared grammar may forbid syntax that a numeric parser accepts", "Plus signs always overflow u8", "It makes the parser multithreaded"], 0,
        "The application's grammar can be narrower than parse::<u8>(). Test the declared syntax as well as the numeric range.",
        "Anything accepted by parse::<u8>() belongs to my format.", "Primitive parsing is a building block; the full record grammar remains your responsibility.",
        [("Partition", "List valid boundaries and independent invalid-input classes."), ("Validate", "Check field count and ASCII decimal syntax before conversion."), ("Reject", "Return a failure rather than panicking or accepting a valid prefix.")],
        "Write a desktop fuzz target that feeds arbitrary bytes through UTF-8 validation and then checks the successful parse contract.")
    lab("projects", "hostile-parser-inputs", "pub fn pair(text: &str) -> Option<(u8, u8)>",
        '    fn byte(s: &str) -> Option<u8> {\n        let s = s.trim();\n        if s.is_empty() || !s.bytes().all(|b| b.is_ascii_digit()) { return None; }\n        s.parse().ok()\n    }\n    let (left, right) = text.split_once(\':\')?;\n    Some((byte(left)?, byte(right)?))',
        [('solution::pair("12:34")', 'Some((12, 34))'), ('solution::pair(" 0 : 255 ")', 'Some((0, 255))'), ('solution::pair("1:2:3")', 'None'), ('solution::pair("256:0")', 'None'), ('solution::pair("-1:2")', 'None'), ('solution::pair("+1:2")', 'None'), ('solution::pair(":2")', 'None'), ('solution::pair("１:2")', 'None')],
        "Parse exactly two trimmed ASCII-decimal u8 fields separated by one colon. Reject signs, empty fields, extra fields, non-ASCII digits, and overflow. Return None on invalid input.", mutant="None")

    lesson("projects", "reliability-labs", "unicode-regression-tests", "Keep a Unicode Regression", "A minimal failure that survives a refactor",
        "Turn a real boundary failure into a small, named case that protects future changes.",
        "Define the unit before testing a text limit: bytes, scalar values, and grapheme clusters differ.", [
        "Suppose a preview function once sliced text at a byte offset and panicked on an accented character. Replacing it with a character iterator fixes that specific bug, but keep a regression that would fail under the old implementation. A test named after the behavior, such as truncates_at_scalar_boundary, is more useful than one named after an unrelated ticket number.",
        "The contract here is to keep at most n Unicode scalar values and add no ellipsis. Return all text when it is shorter than n, and an empty string when n is zero. This is not a display-column limit or a grapheme-cluster limit. An e followed by a combining accent consists of two scalar values; stopping after one may produce a visually surprising but contractually valid result. A user-interface preview may need a grapheme-aware library instead.",
        "A strong regression set contains the smallest original failure, zero, an empty input, an oversized limit, and a neighboring ASCII case. Add a property that the result is a prefix at a valid UTF-8 boundary and contains at most the requested number of scalar values. Avoid assuming that String::len counts characters; it counts bytes.",
        "Local compiler profile: standard library only. The lab compiles the changed function and checks the regression cases independently. Before changing the contract to add an ellipsis, decide whether the ellipsis counts toward the limit and whether existing callers depend on exact output. Good tests document that contract; they should not freeze every internal implementation choice or discourage a clearer iterator-based solution."
        ], 'fn prefix(text: &str, n: usize) -> String { text.chars().take(n).collect() }\nfn main() {\n    assert_eq!(prefix("É🦀rust", 2), "É🦀");\n    assert_eq!(prefix("abc", 0), "");\n}',
        "Keep a prefix measured in Unicode scalar values without byte slicing.",
        "How many Unicode scalar values are in e followed by a combining accent?",
        ["One in every representation", "Two, although they may render as one grapheme", "The UTF-8 byte length is always the scalar count"], 1,
        "A scalar value and a grapheme are different units. State and test the intended unit explicitly.",
        "chars().count() always measures visible character width.", "Scalar values can combine into a grapheme and have different display widths.",
        [("Reproduce", "Keep the smallest input that broke byte slicing."), ("Specify", "Define zero, short input, and the Unicode unit."), ("Protect", "Retain the regression while allowing the implementation to change.")],
        "Design a grapheme-aware version for desktop Cargo. Explain how its output differs for combining accents and emoji sequences.")
    lab("projects", "unicode-regression-tests", "pub fn prefix(text: &str, n: usize) -> String",
        '    text.chars().take(n).collect()',
        [('solution::prefix("É🦀rust", 2)', '"É🦀"'), ('solution::prefix("abc", 0)', '""'), ('solution::prefix("", 3)', '""'), ('solution::prefix("ab", 9)', '"ab"'), ('solution::prefix("e\\u{301}x", 1)', '"e"')],
        "Return at most n Unicode scalar values from the start, with no ellipsis. Never slice at an unchecked byte offset.", mutant="String::new()")


def add_async(unit, lesson):
    unit("concurrency", "async-operations", "Async Operations", "Own tasks, bound concurrency, and shut down deliberately")
    profile = 'Desktop Cargo profile: use `tokio = { version = "1", default-features = false, features = ["rt", "sync"] }`. These examples build a current-thread runtime explicitly and need no Tokio procedural macros, sockets, timers, signals, or multi-thread scheduler. A current-thread executor can run concurrent futures but does not provide CPU parallelism. In Crabrix, consult the prepared Cargo compatibility report before running the project; this reading is not a promise that every Tokio feature works in a WASI guest.'
    lesson("concurrency", "async-operations", "joinset-task-ownership", "Own Tasks with JoinSet", "Completion order, errors, and task lifetime",
        "Keep the tasks you start in a collection whose lifetime and results are explicit.",
        "Spawning starts an independent task; awaiting its result is a separate responsibility.", [
        "An async function creates a future, while spawning places that future under a runtime's scheduler. If your operation starts several child tasks, decide who owns their handles and who observes failures. JoinSet groups tasks returning the same type and yields their results in completion order. That order is not necessarily the order in which the tasks were inserted.",
        "The example associates each result with its input index, drains the set with join_next, and sorts the collected pairs before presenting them. The sorting is a deliberate presentation policy, not an assumption about scheduler order. Handle the outer JoinError separately from any application Result returned inside a task: a task panic and a rejected input are different failures.",
        "Dropping a JoinSet aborts its remaining tasks. This makes ownership visible, but abort is not a business-level rollback and does not undo effects already performed. A spawned blocking operation can have additional cancellation limitations. A reliable operation either drains its children, cancels them according to an explicit policy, or transfers their ownership to a longer-lived component.",
        profile,
        "For practice, make one child return an application error without panicking. Then make a different child panic and compare the two error layers. Do not require an exact completion sequence in the test; verify the set of indexed results. Keep real network work out of this exercise so scheduling behavior is not confused with a server or a backend execution service."
        ], 'use tokio::{runtime::Builder, task::JoinSet};\nfn main() {\n    let rt = Builder::new_current_thread().build().unwrap();\n    rt.block_on(async {\n        let mut tasks = JoinSet::new();\n        for n in 0..4 { tasks.spawn(async move { (n, n * n) }); }\n        let mut results = Vec::new();\n        while let Some(result) = tasks.join_next().await { results.push(result.unwrap()); }\n        results.sort_unstable();\n        assert_eq!(results, [(0, 0), (1, 1), (2, 4), (3, 9)]);\n    });\n}',
        "Run the declared desktop Cargo example. Add a Result-valued task and handle application errors independently from JoinError.",
        "In which order does JoinSet yield completed tasks?",
        ["Insertion order in every runtime", "Completion order, which may differ from insertion order", "Always sorted by return value"], 1,
        "JoinSet yields completed tasks. Preserve an index if the application needs a stable presentation order.",
        "Dropping every task handle is a graceful shutdown protocol.", "An explicit owner must decide whether to wait, request cancellation, or abort; prior effects are not rolled back.",
        [("Start", "Keep task ownership in one JoinSet."), ("Observe", "Distinguish JoinError from application errors."), ("Finish", "Drain results or explicitly cancel remaining tasks.")],
        "Document what happens when one task fails after another has written a report. Do not describe abort as rollback.", 20)
    lesson("concurrency", "async-operations", "semaphore-backpressure", "Bound Work Before Spawning", "Semaphore permits and bounded queues",
        "Put the limit before the expensive resource allocation, not after an unbounded queue has formed.",
        "A concurrency limit and a queue-size limit protect different resources.", [
        "A semaphore grants a finite number of permits. Holding a permit across the protected operation bounds the number of simultaneous operations. The important design question is where that permit is acquired. Spawning a million tasks that each wait for a permit still allocates a million waiting tasks; the semaphore has limited active work but has not bounded queued memory.",
        "Acquire an owned permit before spawning each job when the producer should wait for capacity. Move the permit into the task and let it drop when that task finishes. This is backpressure: a fast producer cannot keep advancing independently of the consumer capacity. For a long-lived producer/consumer system, use a bounded channel as well, and decide whether a full queue waits, rejects, or drops according to the product's contract.",
        "The example has six small jobs and two permits. It drains the JoinSet after submission and checks that every job completed. Because the runtime is current-thread, waiting for a permit yields so earlier jobs can run. Real I/O can overlap, but CPU-bound work does not become parallel here. A permit must cover the resource usage you intend to limit; releasing it before the expensive operation defeats that limit.",
        profile,
        "Test the policy using observable counters and an explicit barrier or yield, not timing guesses. Assert that the active count never exceeds the permit count and that every acquired permit is eventually returned after error paths. Do not use a zero-permit semaphore as a normal concurrency setting unless some other component will intentionally release capacity."
        ], 'use std::sync::Arc;\nuse tokio::{runtime::Builder, sync::Semaphore, task::JoinSet};\nfn main() {\n    Builder::new_current_thread().build().unwrap().block_on(async {\n        let limit = Arc::new(Semaphore::new(2));\n        let mut tasks = JoinSet::new();\n        for n in 0..6 {\n            let permit = limit.clone().acquire_owned().await.unwrap();\n            tasks.spawn(async move {\n                let _permit = permit;\n                tokio::task::yield_now().await;\n                n * 2\n            });\n        }\n        let mut results = Vec::new();\n        while let Some(value) = tasks.join_next().await { results.push(value.unwrap()); }\n        results.sort_unstable();\n        assert_eq!(results, [0, 2, 4, 6, 8, 10]);\n        assert_eq!(limit.available_permits(), 2);\n    });\n}',
        "Run the declared desktop Cargo example. Instrument active work and verify a peak no greater than two without relying on sleeps.",
        "Does acquiring a permit inside each of a million already-spawned tasks bound queued-task memory?",
        ["No; active work is bounded, but all those waiting tasks still exist", "Yes; waiting tasks consume no memory", "Only when the jobs return integers"], 0,
        "Bound production before spawning or use a bounded queue; limiting active work alone does not limit waiting tasks.",
        "A semaphore automatically bounds every allocation in a pipeline.", "Capacity must be applied at the relevant allocation boundary and combined with a queue policy.",
        [("Reserve", "Await capacity before creating another task."), ("Hold", "Move the owned permit into the protected operation."), ("Release", "Let RAII return capacity on success and ordinary error paths.")],
        "Add a bounded channel between input and workers, then specify what the UI should do when the channel is full.", 20)
    lesson("concurrency", "async-operations", "graceful-shutdown-protocol", "A Graceful Shutdown Protocol", "Stop admission, signal, and wait",
        "Cancellation becomes reliable when the operation owns a protocol and a completion point.",
        "Requesting shutdown is not the same as observing that all workers have stopped.", [
        "A useful shutdown sequence has three responsibilities: decide that shutdown is needed, notify the components that own work, and wait for their completion. Before signaling workers, stop accepting new work so the system cannot refill its queue forever. Then decide whether already accepted work is drained, rejected with an explicit result, or interrupted at a documented safe point.",
        "The example uses a watch channel carrying a persistent boolean state. Each worker subscribes before the request and observes the current value before waiting for a change. That first check matters: a worker that starts after the value became true must not wait forever for another update. A watch channel represents the latest state, not a queue containing one shutdown message per worker.",
        "After sending the request, the owner drains JoinSet and confirms that both workers acknowledged shutdown. This is deliberately an in-memory example without operating-system signals. A desktop service can translate ctrl-c into the same protocol, while a UI can translate an explicit Cancel action. The cancellation source and the worker contract remain separate so the protocol can be tested without terminating the process.",
        profile,
        "A real service also needs a deadline and escalation policy for stuck workers. Aborting a task is not a substitute for safe cancellation of a transaction or a blocking operation. Keep partial progress visible, release permits with RAII, and do not report that a save completed merely because the worker future was dropped. Test shutdown requested before subscription, during idle work, and after completion."
        ], 'use tokio::{runtime::Builder, sync::watch, task::JoinSet};\nfn main() {\n    Builder::new_current_thread().build().unwrap().block_on(async {\n        let (stop, receiver) = watch::channel(false);\n        let mut tasks = JoinSet::new();\n        for _ in 0..2 {\n            let mut rx = receiver.clone();\n            tasks.spawn(async move {\n                loop {\n                    if *rx.borrow() { break; }\n                    if rx.changed().await.is_err() { break; }\n                }\n                "stopped"\n            });\n        }\n        stop.send(true).unwrap();\n        let mut stopped = 0;\n        while let Some(result) = tasks.join_next().await {\n            assert_eq!(result.unwrap(), "stopped");\n            stopped += 1;\n        }\n        assert_eq!(stopped, 2);\n    });\n}',
        "Run the declared desktop Cargo example. Request shutdown before spawning a late worker and verify it observes the current state immediately.",
        "Why check the current watch value before awaiting changed()?",
        ["It provides CPU parallelism", "It prevents shutdown requested earlier from being missed by a late worker", "It serializes every file on the server"], 1,
        "Shutdown is persistent state. A late subscriber must inspect the current value instead of waiting for a future change that may never arrive.",
        "Sending a stop signal proves that every worker has finished.", "The owner must also observe task completion, and define a policy for workers that do not cooperate.",
        [("Stop admission", "Prevent new accepted jobs while shutdown is underway."), ("Notify", "Publish persistent shutdown state to each worker."), ("Wait", "Join every worker and handle failures before reporting completion.")],
        "Write down a deadline and escalation policy for a worker that never reaches a cancellation point. Label which steps require a desktop timer or host support.", 20)


def add_wasm(unit, lesson, lab):
    unit("systems", "wasm-wasi", "Rust, WASM & WASI", "Separate the language, the module, and the host's authority")
    lesson("systems", "wasm-wasi", "wasm-host-boundaries", "WASM Is Not the Browser API", "Targets, host imports, and local execution",
        "A WebAssembly module runs with the imports its host supplies, not with every capability of the computer.",
        "Compilation target and host imports determine what a module can do.", [
        "Rust is the source language; WebAssembly is an execution format; WASI is a family of host interfaces. They are separate layers. A module targeting wasm32-unknown-unknown does not automatically get a filesystem, sockets, or the browser DOM. A wasm32-wasip1 program expects the corresponding WASI imports, which a browser does not provide merely by supporting WebAssembly.",
        "Crabrix supplies a local runtime and its supported host interfaces. In the browser, a worker and runtime adapter can compile or execute locally while the website serves toolchain assets. Downloading a compiler is network activity, but it is different from sending source to a backend compiler. Shared documents can use a relay without granting another participant the right to execute source on your device.",
        "A browser DOM integration needs a JavaScript boundary or another deliberate adapter. A guest filesystem is likewise a host-provided view; its paths are not unrestricted paths on the phone. If a library assumes operating-system processes, native threads, or unsupported networking imports, having Rust source alone does not make it compatible with this target.",
        "Local compiler profile for this lesson's small exercise: standard-library text inspection only. The exercise classifies import names according to an explicitly supplied allowlist; it does not inspect a real module or implement a security policy. Real runtime validation must parse the binary, check actual imports and limits, and preserve the host's sandbox. Keep educational models distinct from the enforcement used by a production engine."
        ], 'fn main() {\n    let declared = ["fd_write", "path_open"];\n    let allowed = ["fd_write"];\n    assert!(declared.iter().any(|name| !allowed.contains(name)));\n}',
        "Model an exact allowlist check without claiming to validate a WASM binary.",
        "Does browser WebAssembly support automatically supply WASI filesystem imports?",
        ["Yes, including the user's entire disk", "No; the embedding host must supply the expected imports", "Only when the source was Rust"], 1,
        "The host supplies imports and authority. WebAssembly support alone does not supply a WASI environment.",
        "A Rust wasm file can call every browser and operating-system API.", "The chosen target and embedding determine the available interfaces.",
        [("Target", "Identify the module's required ABI and imports."), ("Host", "Check which interfaces and directory grants the runtime supplies."), ("Execute", "Run locally only after the local user initiates execution.")],
        "Explain why serving a compiler asset, relaying an encrypted document, and executing user source are three separate operations.")
    lab("systems", "wasm-host-boundaries", "pub fn permitted(imports: &[&str], allowed: &[&str]) -> bool",
        '    imports.iter().all(|name| allowed.contains(name))',
        [('solution::permitted(&["fd_write"], &["fd_write"])', 'true'), ('solution::permitted(&[], &[])', 'true'), ('solution::permitted(&["path_open"], &["fd_write"])', 'false'), ('solution::permitted(&["fd_write_extra"], &["fd_write"])', 'false'), ('solution::permitted(&["fd_write", "path_open"], &["fd_write"])', 'false')],
        "For this educational model, return true exactly when every import name occurs verbatim in allowed. Empty imports pass. Do not use prefix matching. This function is not a real WASM verifier.", mutant="true")

    lesson("systems", "wasm-wasi", "wasm-linear-memory", "Linear Memory Boundaries", "Checked offsets, lengths, and borrowed slices",
        "A guest pointer is an offset into guest memory, not a host pointer you can blindly dereference.",
        "Check offset plus length without overflow before making a borrowed view.", [
        "A host function receiving a guest pointer and length must interpret them relative to that module's current linear memory. First validate the requested range, then borrow only the verified bytes. An offset is not a native pointer, and a numerically small address does not establish permission. A length can overflow when added to the offset even if each input separately fits its integer type.",
        "The lab models this boundary with a Rust byte slice and usize offsets. Use checked_add for the end offset and slice::get for the bounds check. Return None for overflow or an out-of-range end. An empty range at memory.len is valid, while an empty range beginning after memory.len is invalid. This precise convention avoids special-case pointer arithmetic that accidentally accepts an invalid start.",
        "Decoding text is a second check. A valid byte range can contain invalid UTF-8, so use from_utf8 if the interface requires text. Do not reinterpret arbitrary guest bytes as a Rust struct whose alignment, layout, or validity requirements may not hold. Copy or decode a documented wire representation instead.",
        "Local compiler profile: standard library only. The model uses no unsafe code and does not implement a runtime memory manager. In a real embedding, memory growth and reentrant calls may invalidate a cached host view, so follow the runtime's borrowing rules and reacquire the view at the appropriate boundary. Tests of this pure function do not establish that a separate native runtime binding follows those rules."
        ], 'fn window(memory: &[u8], offset: usize, len: usize) -> Option<&[u8]> {\n    let end = offset.checked_add(len)?;\n    memory.get(offset..end)\n}\nfn main() {\n    assert_eq!(window(b"crab", 1, 2), Some(&b"ra"[..]));\n    assert_eq!(window(b"crab", usize::MAX, 2), None);\n}',
        "Implement a safe range model including zero-length and overflow boundaries.",
        "Is an in-bounds byte slice necessarily valid UTF-8?",
        ["No; text decoding requires another validation step", "Yes, because all memory is UTF-8", "Only if its length is even"], 0,
        "Range validity and text validity are separate contracts. Validate the range, then decode if text is required.",
        "Checking the start offset alone makes the entire range safe.", "The sum can overflow and the end can exceed memory even when the start is valid.",
        [("Add", "Compute the end with checked arithmetic."), ("Borrow", "Use get to check the complete range."), ("Decode", "Validate UTF-8 or another wire format separately.")],
        "Explain why a host view obtained before a reentrant guest call may need to be reacquired afterward.")
    lab("systems", "wasm-linear-memory", "pub fn window(memory: &[u8], offset: usize, len: usize) -> Option<&[u8]>",
        '    let end = offset.checked_add(len)?;\n    memory.get(offset..end)',
        [('solution::window(b"crab", 1, 2)', 'Some(&b"ra"[..])'), ('solution::window(b"crab", 4, 0)', 'Some(&b""[..])'), ('solution::window(b"crab", 5, 0)', 'None'), ('solution::window(b"crab", usize::MAX, 2)', 'None'), ('solution::window(b"crab", 3, 2)', 'None')],
        "Borrow the requested byte range or return None. Check addition overflow. A zero-length range at the end is valid; a start past the end is not.", mutant="None")

    lesson("systems", "wasm-wasi", "runtime-resource-budgets", "Budget a Local Runtime", "Independent CPU, memory, output, and storage limits",
        "Local execution still needs independent limits for the resources a guest can consume.",
        "A timeout does not replace memory, output, or filesystem quotas.", [
        "A local playground executes untrusted source on the user's own device, so a useful sandbox must bound more than filesystem access. A program can loop forever, allocate aggressively, print without end, or fill its writable directory. Each consumes a different resource. A wall-clock deadline alone may detect a slow run only after memory or output has already exhausted the host.",
        "Define budgets at the layer that owns the resource. An interpreter may provide fuel or interruption for instruction execution; the host can cap captured output and writable bytes; the embedding can limit memory pages and concurrent runs. Cancellation should release the owned run and its resources, while the UI reports a quota stop distinctly from a successful program exit or an ordinary Rust diagnostic.",
        "The compiler lab is a small model of output accounting. Starting from a known usage, accept the next chunk only if checked addition stays within an inclusive limit. Refuse overflow and an already-invalid starting state. An empty chunk at the exact limit is valid. This function does not enforce the actual runtime's limits; it teaches why checking after an unbounded allocation is too late.",
        "Local compiler profile: standard library only. In a shared Playground, code and selection changes may be interactive while execution remains local and explicit. Another participant's Run should update shared output metadata rather than start your device's compiler. A production safety review must test those event boundaries separately from this arithmetic model, including disconnection, repeated messages, and a local cancel during remote edits."
        ], 'fn reserve(used: usize, next: usize, limit: usize) -> Option<usize> {\n    let total = used.checked_add(next)?;\n    (total <= limit).then_some(total)\n}\nfn main() {\n    assert_eq!(reserve(8, 2, 10), Some(10));\n    assert_eq!(reserve(8, 3, 10), None);\n}',
        "Implement inclusive byte-budget accounting with overflow protection.",
        "Which statement about a local execution timeout is correct?",
        ["It makes all allocations safe before it fires", "It automatically limits printed output to one line", "It is one limit and does not replace separate resource quotas"], 2,
        "CPU time, memory, output, storage, and concurrency need limits at their own boundaries.",
        "A program is harmless to local resources because it never runs on the backend.", "Local execution avoids backend computation but still consumes the device's resources.",
        [("Measure", "Identify the independently consumed resource."), ("Reserve", "Check an inclusive limit before accepting another chunk."), ("Stop", "Report quota termination and release the local run.")],
        "Design a test matrix distinguishing a Rust panic, compilation error, user cancel, CPU budget, output cap, and writable-storage cap.")
    lab("systems", "runtime-resource-budgets", "pub fn reserve(used: usize, next: usize, limit: usize) -> Option<usize>",
        '    let total = used.checked_add(next)?;\n    (total <= limit).then_some(total)',
        [('solution::reserve(8, 2, 10)', 'Some(10)'), ('solution::reserve(10, 0, 10)', 'Some(10)'), ('solution::reserve(8, 3, 10)', 'None'), ('solution::reserve(11, 0, 10)', 'None'), ('solution::reserve(usize::MAX, 1, usize::MAX)', 'None')],
        "Return updated usage only when checked addition succeeds and the inclusive limit is respected. Reject an invalid starting usage as well as overflow.", mutant="None")
