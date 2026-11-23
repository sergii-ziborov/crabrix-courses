ID = "c-integer-overflow-and-casts"
UNIT = "c-syntax"
ORDER = 2

FROM_CODE = r'''#include <stdint.h>
#include <stdio.h>

static int32_t add(int32_t a, int32_t b) { return a + b; } /* overflow is UB */

int main(void) {
    uint32_t count = 65536, size = 65536;
    uint32_t bytes = count * size;  /* unsigned: wraps to 0, no error */
    uint8_t byte = (uint8_t)300;    /* keeps the low 8 bits: 44 */
    int d = -1;
    unsigned u = 3;
    printf("bytes=%u byte=%u\n", bytes, byte);
    printf("-1 < 3u is %d\n", d < u); /* d converts to UINT_MAX: 0 */
    printf("%d\n", add(INT32_MAX, 1)); /* UBSan: signed integer overflow */
    return 0;
}
'''

EXAMPLE = r'''fn main() {
    let count: u32 = 65_536;
    let size: u32 = 65_536;
    println!("{:?}", count.checked_mul(size));   // None: overflow is a value
    println!("{}", count.wrapping_mul(size));     // 0: wrapping, when you mean it
    println!("{}", 300_i32 as u8);                // 44: `as` truncates integers
    println!("{:?}", u8::try_from(300_i32).ok()); // None: a checked conversion
    println!("{}", 3.9e10_f64 as i32);            // 2147483647: float casts saturate
    let d: i32 = -1;
    let u: u32 = 3;
    println!("{}", i64::from(d) < i64::from(u));  // true: widen both sides yourself
}
'''

PRACTICE = r'''fn main() {
    let u: u32 = 3;
    let d: i32 = -1;
    println!("{}", d < u);
}
'''

LESSON = {
    "title": "Integer Overflow and Casts",
    "concept": "Defined overflow policy and explicit conversions",
    "minutes": 12,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "Rust never converts between integer types silently, and overflow is always defined: a panic in debug builds, wrapping in release builds, or exactly the policy you call.",
        "rule": "Integer types never mix implicitly; choose the overflow policy (`checked_`, `wrapping_`, `saturating_`) and the conversion (`From`, `TryFrom`, `as`) explicitly.",
        "explanation": (
            "C's usual arithmetic conversions decide behind your back: in `-1 < 3u` the `int` becomes `UINT_MAX` and the comparison is false, and clang's `-Wsign-compare` is the only hint. Rust has no integer promotion and no implicit conversion between `i32`, `u32`, `usize` or any other pair. Comparing or adding mixed types is error `E0308`. Widen with `i64::from(d)`, which cannot fail, or convert with `u8::try_from(x)`, which returns a `Result` when the value might not fit.\n\n"
            "Signed overflow in C is undefined behaviour: UBSan reports `signed integer overflow: 2147483647 + 1 cannot be represented in type 'int32_t'`, and the optimiser may assume it never happens. In Rust overflow is always defined. In the default debug profile arithmetic is checked, and overflow panics with `attempt to add with overflow`. The release profile turns `overflow-checks` off, and the same expression wraps in two's complement. Neither is undefined, but a program that depends on either for ordinary values has a bug.\n\n"
            "When overflow is possible, say what you want. `checked_mul` returns `None`, `wrapping_mul` wraps on purpose (hashes, checksums), `saturating_add` clamps at the limit, and `overflowing_add` returns the wrapped value with a flag. The policy is then visible in the code instead of depending on the build profile.\n\n"
            "`as` remains for deliberate, lossy casts. Between integers it truncates or extends like a C cast: `300_i32 as u8` is 44. From floating point it saturates, and NaN becomes 0, where C is undefined for out-of-range values. Use `as` when you mean exactly that, and `TryFrom` when a value that does not fit is an error."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "Each line chooses its policy: `None` from `checked_mul`, deliberate wrapping, a truncating `as`, a checked conversion, a saturating float cast and an explicit widening.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C functions without their silent wrap and truncation: `total_bytes` returns `None` when `count * size` does not fit in `u32`, and `to_byte` returns `None` for values outside `0..=255`.",
        "success": "`total_bytes(65_536, 65_536)` is `None`, `to_byte(300)` and `to_byte(-1)` are `None`, and values that fit come back unchanged.",
        "question": "In C, `d < u` with `int d = -1` and `unsigned u = 3` is false. What does rustc do with the same comparison on an `i32` and a `u32`?",
        "answers": [
            "Rejects it with `E0308`: you must convert one side yourself",
            "Converts `d` to `u32` and returns `false`, like C",
            "Converts both to `i64` and returns `true`",
            "Compiles, then panics at run time because `d` is negative",
        ],
        "correctAnswer": 0,
        "feedback": "Rust has no usual arithmetic conversions. `i64::from(d) < i64::from(u)` states the widening and evaluates to `true`.",
        "recall": [
            {
                "question": "A debug build panics with `attempt to multiply with overflow`. Does the release build of the same code have undefined behaviour?",
                "answer": "No. With the default release profile, `overflow-checks` is off and the multiplication wraps in two's complement, which is defined but almost certainly wrong. Call `checked_mul`, or `wrapping_mul` if wrapping is intended, so both builds behave the same.",
            },
            {
                "question": "What do these four casts produce?",
                "code": "let a = 300_i32 as u8;\nlet b = -1_i32 as u32;\nlet c = 3.9e10_f64 as i32;\nlet d = f64::NAN as i32;\nprintln!(\"{a} {b} {c} {d}\");",
                "answer": "`44 4294967295 2147483647 0`. Integer casts keep or reinterpret the low bits as in C. Float-to-integer casts saturate and map NaN to 0; in C those two out-of-range conversions are undefined.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Find the mixed types", "detail": "Every C expression that mixes signedness or width becomes a compile error in Rust; decide which side to convert."},
            {"title": "Pick the policy", "detail": "For each `+`, `*` or `-` that can exceed the type, choose `checked_`, `wrapping_` or `saturating_`, or prove the bound."},
            {"title": "Separate casts from conversions", "detail": "Keep `as` for intended truncation; use `TryFrom` where an out-of-range value is an error."},
        ],
        "misconception": "“Overflow in Rust is like unsigned overflow in C: it silently wraps.”",
        "correction": "Only in release builds with the default profile, and even there it is a defined wrap rather than undefined behaviour. Debug builds panic. Code that needs wrapping should call `wrapping_*` so it does not depend on the build profile.",
        "transferChallenge": "Write `midpoint(lo: u32, hi: u32) -> u32` without `(lo + hi) / 2`, then test it with `u32::MAX - 1` and `u32::MAX`.",
        "connections": [
            {"direction": "previous", "title": "const by Default", "concept": "Immutable bindings, mut and shadowing"},
            {"direction": "next", "title": "Functions Are Expressions", "concept": "Tail values replace return and the ternary"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "Unsigned overflow wraps to 0, `(uint8_t)300` keeps the low byte, `-1 < 3u` is false, and `add(INT32_MAX, 1)` is undefined behaviour that UBSan reports.",
        "contrasts": [
            {"from": "Signed overflow is undefined; unsigned overflow wraps silently.",
             "rust": "Overflow panics in debug builds and wraps in release; `checked_*` makes it a value."},
            {"from": "Usual arithmetic conversions mix signed and unsigned silently.",
             "rust": "Mixed integer types do not compile (`E0308`); convert with `From`, `TryFrom` or `as`."},
            {"from": "An out-of-range float-to-integer conversion is undefined.",
             "rust": "`f64 as i32` saturates, and NaN becomes 0."},
        ],
        "credits": ["basics/number-types", "basics/operators"],
    },
}

CHALLENGE = {
    "functions": ["total_bytes", "to_byte"],
    "source": r'''// C original:
// uint32_t total_bytes(uint32_t count, uint32_t size) { return count * size; } /* wraps */
// uint8_t to_byte(int value) { return (uint8_t)value; }               /* keeps the low byte */
pub fn total_bytes(count: u32, size: u32) -> Option<u32> {
    todo!("implement the contract")
}

pub fn to_byte(value: i32) -> Option<u8> {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;

fn main() {
    assert_eq!(solution::total_bytes(3, 4), Some(12), "case 1");
    assert_eq!(solution::total_bytes(0, u32::MAX), Some(0), "case 2");
    assert_eq!(solution::total_bytes(65_536, 65_536), None, "case 3");
    assert_eq!(solution::total_bytes(65_535, 65_537), Some(u32::MAX), "case 4");
    assert_eq!(solution::to_byte(255), Some(255), "case 5");
    assert_eq!(solution::to_byte(300), None, "case 6");
    assert_eq!(solution::to_byte(-1), None, "case 7");

    println!("PASS c-integer-overflow-and-casts");
}
''',
    "cases": [
        ("visible", "solution::total_bytes(3, 4)", "Some(12)"),
        ("boundary", "solution::total_bytes(0, u32::MAX)", "Some(0)"),
        ("semantic", "solution::total_bytes(65_536, 65_536)", "None"),
        ("boundary", "solution::total_bytes(65_535, 65_537)", "Some(u32::MAX)"),
        ("visible", "solution::to_byte(255)", "Some(255)"),
        ("semantic", "solution::to_byte(300)", "None"),
        ("boundary", "solution::to_byte(-1)", "None"),
    ],
}

EXPECT = {
    "example": "None\n0\n44\nNone\n2147483647\ntrue\n",
    "practice": {"errors": ["E0308"]},
    "recall": [None, {"stdout": "44 4294967295 2147483647 0\n"}],
    "c": {"warnings": ["-Wsign-compare"], "stdout": "bytes=0 byte=44\n-1 < 3u is 0\n-2147483648\n",
          "exit": 0, "sanitize": "undefined",
          "finding": "signed integer overflow: 2147483647 + 1 cannot be represented in type"},
    "wrong": {
        "c-integer-overflow-and-casts.1.rs": {"mode": "panic", "note": "C habit: `wrapping_mul` and `value as u8` keep the silent wrap and truncation"},
        "c-integer-overflow-and-casts.2.rs": {"mode": "panic", "note": "plain `count * size` panics in debug builds and wraps in release builds"},
    },
}
