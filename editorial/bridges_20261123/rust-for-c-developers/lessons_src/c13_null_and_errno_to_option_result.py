ID = "c-null-and-errno-to-option-result"
UNIT = "c-data"
ORDER = 2

FROM_CODE = r'''#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

/* Returns -1 and sets errno on failure. But "-1" is also a valid input. */
static long parse_count(const char *text) {
    char *end;
    errno = 0;                       /* strtol sets errno only on failure */
    long value = strtol(text, &end, 10);
    if (end == text || *end != '\0') {
        errno = EINVAL;
        return -1;
    }
    return value;                    /* on ERANGE: LONG_MAX or LONG_MIN */
}

int main(void) {
    long ok = parse_count("42");
    long bad = parse_count("4x");
    int bad_errno = errno;
    long minus = parse_count("-1");  /* the same -1, with errno == 0 */
    printf("%ld %ld(errno=%d) %ld(errno=%d)\n", ok, bad, bad_errno, minus, errno);
    const char *dir = getenv("CRABRIX_EXAMPLE_UNSET"); /* NULL when absent */
    printf("%s\n", dir ? dir : "(not set)");            /* forget the check: crash */
    return 0;
}
'''

EXAMPLE = r'''use std::num::ParseIntError;

fn parse_count(text: &str) -> Result<i64, ParseIntError> {
    text.parse::<i64>() // the error is the return value, not a global
}

fn sum_counts(a: &str, b: &str) -> Result<i64, ParseIntError> {
    Ok(parse_count(a)? + parse_count(b)?) // `?` returns the first error
}

fn main() {
    println!("{:?}", parse_count("42"));
    println!("{:?}", parse_count("4x"));
    println!("{:?}", parse_count("-1")); // Ok(-1): no confusion with failure
    match std::env::var_os("CRABRIX_EXAMPLE_UNSET") {
        Some(dir) => println!("{dir:?}"),
        None => println!("(not set)"), // absence must be handled
    }
    println!("{:?} {:?}", sum_counts("40", "2"), sum_counts("40", "x"));
}
'''

PRACTICE = r'''fn find_port(config: &[(&str, u16)]) -> Option<u16> {
    config.iter().find(|(key, _)| *key == "port").map(|(_, value)| *value)
}

fn main() {
    let config = [("host", 80)];
    let port: u16 = find_port(&config);
    println!("{}", port + 1);
}
'''

LESSON = {
    "title": "NULL and errno to Option and Result",
    "concept": "Absence and failure in the return type",
    "minutes": 13,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "Absence is `Option<T>` and failure is `Result<T, E>`, both in the return type, so a caller cannot use the value without handling the other case.",
        "rule": "Return `Option<T>` when a value may simply be absent and `Result<T, E>` when the caller needs to know why an operation failed.",
        "explanation": (
            "C signals trouble out of band. A pointer return uses `NULL` for absent, as `getenv` and `strchr` do. An integer return reserves a value such as `-1` and leaves the reason in `errno`, which must be cleared before calls such as `strtol` and read before the next library call can overwrite it. In the example, `-1` means failure and is also a valid parsed value, so the caller has to inspect `errno` to tell them apart.\n\n"
            "Rust puts both into the type. `Option<T>` is `Some(value)` or `None`; `Result<T, E>` is `Ok(value)` or `Err(error)`. You cannot use the `T` inside without saying what happens in the other case: `let port: u16 = find_port(&config);` is error `E0308`, because the function returns `Option<u16>`. References are never null, so `Option<&T>` is the nullable pointer, with the same size as a plain reference.\n\n"
            "Choose by what the caller needs. A lookup that may find nothing returns `Option`. Parsing external text, I/O and anything with several distinct causes of failure return `Result` with an error type that names them, often an `enum` such as `PortError`. The `?` operator replaces the `if (rc < 0) return rc;` ladder: it returns the error to the caller and unwraps the success value.\n\n"
            "`unwrap()` and `expect(...)` turn `None` or `Err` into a panic. They belong in tests, examples and states that are truly impossible; for expected failures such as invalid input, return the `Result`. Unlike `errno`, an error value cannot be overwritten by a later call, and it travels with the result it describes."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "`parse_count` returns its error as a value, `-1` parses as `Ok(-1)`, an unset variable is `None`, and `?` passes the first failure up.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C `parse_port`: return `Empty` for empty text, `NotANumber` if any character is not an ASCII digit (no sign and no spaces, stricter than `strtol`), `OutOfRange` for 0 or anything above 65535, and the port otherwise.",
        "success": "`\"8080\"` parses, `\"+80\"` is `NotANumber`, and `\"0\"`, `\"65536\"` and a 20-digit number are `OutOfRange`.",
        "question": "A C lookup returns `NULL` when a key is missing, and a config parser returns `-1` with `errno` set when a line is malformed. Which Rust return types fit those two cases?",
        "answers": [
            "`Result<T, ()>` for both",
            "`Option<T>` for both, with `None` for any problem",
            "`*const V` for the lookup and `i32` plus a global error code for the parser",
            "`Option<&V>` for the lookup and `Result<Config, ParseError>` for the parser",
        ],
        "correctAnswer": 3,
        "feedback": "A missing key is ordinary absence. A malformed line is a failure the caller should be able to explain or report, so it carries an error value.",
        "recall": [
            {
                "question": "What does `?` do in this function, and what does it return for `\"7\"` and for `\"x\"`?",
                "code": "use std::num::ParseIntError;\n\nfn double(text: &str) -> Result<i32, ParseIntError> {\n    let n: i32 = text.parse()?;\n    Ok(n * 2)\n}\n\nfn main() {\n    println!(\"{:?} {:?}\", double(\"7\"), double(\"x\"));\n}",
                "answer": "On `Err`, `?` returns that error from `double` immediately; on `Ok`, it unwraps the number. It prints `Ok(14) Err(ParseIntError { kind: InvalidDigit })`.",
            },
            {
                "question": "Is `Option<&T>` bigger than a nullable C pointer?",
                "code": "println!(\"{} {}\", size_of::<&u64>(), size_of::<Option<&u64>>());",
                "answer": "No: on a 64-bit target this prints `8 8`. A reference is never null, so the compiler uses the null bit pattern for `None`. You get the representation of a nullable pointer with a check the compiler enforces.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Classify each failure", "detail": "For each C return code or `NULL`, decide whether it is absence (`Option`) or a failure with a reason (`Result`)."},
            {"title": "Name the reasons", "detail": "Turn the `errno` values a function can set into the variants of an error `enum`."},
            {"title": "Propagate with ?", "detail": "Replace each check-and-return ladder with `?` inside a function that returns `Result`."},
        ],
        "misconception": "“`unwrap()` is the Rust way to read a return value.”",
        "correction": "`unwrap()` turns an absent value or an error into a panic. Use it where failure would be a bug; for input that can be invalid, match on the `Result` or return it with `?`.",
        "transferChallenge": "Write `fn parse_endpoint(text: &str) -> Result<(String, u16), EndpointError>` for `host:port` that reuses `parse_port` with `?` through a `From<PortError>` conversion.",
        "connections": [
            {"direction": "previous", "title": "Tagged Unions to Enums", "concept": "A tag that cannot disagree with its payload"},
            {"direction": "next", "title": "char Arrays to Strings", "concept": "Owned UTF-8 with a length, not a NUL"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "`-1` is both the failure marker and a valid result, so the caller must clear and inspect `errno`; `getenv` returns `NULL` when the variable is absent.",
        "contrasts": [
            {"from": "`NULL` means absent, and dereferencing it unchecked compiles.",
             "rust": "`Option<T>` must be matched before the value can be used."},
            {"from": "`-1` plus `errno` signals failure out of band.",
             "rust": "`Result<T, E>` carries the reason in the return value."},
            {"from": "`if (rc < 0) return rc;` after every call.",
             "rust": "`?` returns the error early and unwraps the success value."},
        ],
        "credits": ["basics/option-result", "basics/recoverable-errors"],
    },
}

CHALLENGE = {
    "functions": ["parse_port"],
    "source": r'''// C original:
// /* 0 on success; -1 with errno = EINVAL or ERANGE on failure. */
// int parse_port(const char *text, uint16_t *out) {
//     char *end;
//     errno = 0;
//     long v = strtol(text, &end, 10);   /* also accepts spaces and a sign */
//     if (end == text || *end != '\0') { errno = EINVAL; return -1; }
//     if (errno == ERANGE || v < 1 || v > 65535) { errno = ERANGE; return -1; }
//     *out = (uint16_t)v;
//     return 0;
// }
#[derive(Debug, PartialEq)]
pub enum PortError {
    Empty,
    NotANumber,
    OutOfRange,
}

pub fn parse_port(text: &str) -> Result<u16, PortError> {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;
use solution::PortError;

fn main() {
    assert_eq!(solution::parse_port("8080"), Ok(8080), "case 1");
    assert_eq!(solution::parse_port(""), Err(PortError::Empty), "case 2");
    assert_eq!(solution::parse_port("80a"), Err(PortError::NotANumber), "case 3");
    assert_eq!(solution::parse_port("+80"), Err(PortError::NotANumber), "case 4");
    assert_eq!(solution::parse_port(" 22"), Err(PortError::NotANumber), "case 5");
    assert_eq!(solution::parse_port("0"), Err(PortError::OutOfRange), "case 6");
    assert_eq!(solution::parse_port("65535"), Ok(65535), "case 7");
    assert_eq!(solution::parse_port("65536"), Err(PortError::OutOfRange), "case 8");
    assert_eq!(solution::parse_port("99999999999999999999"), Err(PortError::OutOfRange), "case 9");

    println!("PASS c-null-and-errno-to-option-result");
}
''',
    "cases": [
        ("visible", 'solution::parse_port("8080")', "Ok(8080)"),
        ("boundary", 'solution::parse_port("")', "Err(PortError::Empty)"),
        ("semantic", 'solution::parse_port("80a")', "Err(PortError::NotANumber)"),
        ("semantic", 'solution::parse_port("+80")', "Err(PortError::NotANumber)"),
        ("semantic", 'solution::parse_port(" 22")', "Err(PortError::NotANumber)"),
        ("boundary", 'solution::parse_port("0")', "Err(PortError::OutOfRange)"),
        ("boundary", 'solution::parse_port("65535")', "Ok(65535)"),
        ("boundary", 'solution::parse_port("65536")', "Err(PortError::OutOfRange)"),
        ("boundary", 'solution::parse_port("99999999999999999999")', "Err(PortError::OutOfRange)"),
    ],
}

EXPECT = {
    "example": "Ok(42)\nErr(ParseIntError { kind: InvalidDigit })\nOk(-1)\n(not set)\nOk(42) Err(ParseIntError { kind: InvalidDigit })\n",
    "practice": {"errors": ["E0308"]},
    "recall": [{"stdout": "Ok(14) Err(ParseIntError { kind: InvalidDigit })\n"}, {"stdout": "8 8\n"}],
    "c": {"warnings": [], "stdout": "42 -1(errno=22) -1(errno=0)\n(not set)\n", "exit": 0},
    "wrong": {
        "c-null-and-errno-to-option-result.1.rs": {"mode": "panic", "note": "`text.parse::<u16>()` with every error mapped to `NotANumber`: accepts `+80` and misreports overflow"},
        "c-null-and-errno-to-option-result.2.rs": {"mode": "panic", "note": "digit check, then `parse::<u32>()`: a 20-digit number overflows `u32` and is reported as `NotANumber`"},
    },
}
