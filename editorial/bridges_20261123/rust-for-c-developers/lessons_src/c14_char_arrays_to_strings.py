ID = "c-char-arrays-to-strings"
UNIT = "c-data"
ORDER = 3

FROM_CODE = r'''#include <ctype.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    const char *word = "café";                 /* UTF-8: c a f 0xC3 0xA9 */
    printf("strlen=%zu\n", strlen(word));       /* 5 bytes, 4 characters */
    char upper[8];
    size_t i = 0;
    for (; word[i]; i++) upper[i] = (char)toupper((unsigned char)word[i]);
    upper[i] = '\0';
    printf("%s\n", upper);                      /* CAFé: toupper sees bytes */
    char name[8];
    strcpy(name, "Margaret");                   /* 9 bytes with the NUL */
    printf("%s\n", name);                       /* ASan: stack-buffer-overflow */
    return 0;
}
'''

EXAMPLE = r'''fn main() {
    let word = "café";
    println!("len={} chars={}", word.len(), word.chars().count()); // bytes vs chars
    println!("{}", word.to_uppercase());    // CAFÉ: Unicode-aware
    println!("{:?}", word.get(0..4));       // None: byte 4 is inside 'é'
    println!("{:?}", word.get(0..3));       // Some("caf")
    let mut name = String::with_capacity(8);
    name.push_str("Margaret");              // grows when needed; no NUL
    name.push_str(" Hamilton");
    println!("{name} ({} bytes)", name.len());
    for (i, c) in word.char_indices() {
        print!("{i}:{c} ");                 // the byte offset of each char
    }
    println!();
}
'''

PRACTICE = r'''fn main() {
    let word = String::from("café");
    let first = word[0];
    println!("{first}");
}
'''

LESSON = {
    "title": "char Arrays to Strings",
    "concept": "Owned UTF-8 with a length, not a NUL",
    "minutes": 12,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "A Rust `String` is an owned, growable UTF-8 buffer with a stored length and no NUL, and text is never indexed by a single integer position.",
        "rule": "`len()` counts UTF-8 bytes and `chars()` yields Unicode scalar values; indexing a string by an integer is forbidden because a byte offset may fall inside a character.",
        "explanation": (
            "C strings are byte arrays ended by a NUL. Their length is a scan (`strlen`), their capacity is whatever the declaration said, and every copy (`strcpy`, `strcat`) trusts the destination to be big enough. In the example, `\"Margaret\"` needs 9 bytes in an 8-byte array: clang warns at compile time that the `strcpy` will always overflow, and AddressSanitizer reports the `stack-buffer-overflow` when it runs.\n\n"
            "`String` owns a heap buffer and stores its length and capacity, so `len()` is O(1), there is no terminator, and `push_str` grows the buffer as needed. `&str` is a borrowed view of UTF-8 bytes, a pointer and a length like a slice; string literals are `&'static str`. Because a Rust string may contain interior NUL bytes and has no terminator, C APIs use `CString` and `CStr` from `std::ffi` instead.\n\n"
            "Rust strings are always valid UTF-8, and that changes how you count. `\"café\".len()` is 5, the bytes, the same as `strlen`; `chars().count()` is 4 Unicode scalar values. A character a person sees can consist of several scalar values, so neither number is always what a reader would count. `toupper` works on bytes and leaves `é` alone; `to_uppercase()` maps Unicode and gives `CAFÉ`.\n\n"
            "`word[0]` does not compile (`E0277`): indexing by an integer would have to pick a byte or a character, and a byte may be half of one. Byte ranges are allowed, as in `&word[0..3]`, but a range that ends inside a character panics. Code that cuts text to a byte budget therefore uses `is_char_boundary`, or `get(range)`, which returns `None` instead of panicking."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "Byte length versus character count, a Unicode-aware uppercase, `get` refusing a cut inside `é`, and a `String` that grows instead of overflowing.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C helpers: `truncate_at_boundary` returns the longest prefix of at most `max_bytes` bytes that ends on a character boundary, and `initials` returns the uppercase first character of each whitespace-separated word.",
        "success": "`truncate_at_boundary(\"café\", 4)` is `\"caf\"` without a panic, and `initials(\"élodie durand\")` is `\"ÉD\"`.",
        "question": "`strlen(\"café\")` is 5 in a UTF-8 C program. What do `\"café\".len()` and `\"café\".chars().count()` return in Rust?",
        "answers": [
            "4 and 4",
            "5 and 4",
            "6 and 5, counting a terminator",
            "4 and 5",
        ],
        "correctAnswer": 1,
        "feedback": "`len()` counts UTF-8 bytes, so `é` contributes two, and there is no terminator. `chars()` yields four scalar values.",
        "recall": [
            {
                "question": "What happens when this runs?",
                "code": "let word = \"café\";\nprintln!(\"{:?}\", word.get(0..4));\nlet cut = &word[0..4];\nprintln!(\"{cut}\");",
                "answer": "It prints `None`, because byte 4 is inside the two-byte `é`, and then the slice `&word[0..4]` panics with `byte index 4 is not a char boundary`. Use `get` or `is_char_boundary` when the offset comes from a byte budget.",
            },
            {
                "question": "Why does Rust pass a `CString` rather than a `&str` to a C function that takes `const char *`?",
                "answer": "A `&str` is not NUL-terminated and may contain interior NUL bytes. `CString::new` rejects interior NULs and appends the terminator, and `as_ptr()` then gives the `const char *` that C expects.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Count in the right unit", "detail": "Decide whether each length is a byte budget (`len()`) or a character count (`chars().count()`)."},
            {"title": "Replace fixed buffers", "detail": "Turn `char buf[N]` plus `strcpy` into a `String` that grows, or check the byte budget explicitly."},
            {"title": "Cut on boundaries", "detail": "Before slicing at a computed byte offset, move it back until `is_char_boundary` is true."},
        ],
        "misconception": "“`chars()` gives the characters a user sees.”",
        "correction": "`chars()` yields Unicode scalar values. A visible character can be several of them, such as `e` followed by a combining accent, or an emoji sequence. Grapheme clusters need a crate such as `unicode-segmentation`.",
        "transferChallenge": "Write `fn ellipsize(text: &str, max_bytes: usize) -> String` that appends `…` when it truncates and still fits the budget, counting the three bytes of `…`.",
        "connections": [
            {"direction": "previous", "title": "NULL and errno to Option and Result", "concept": "Absence and failure in the return type"},
            {"direction": "next", "title": "Headers and make to Cargo", "concept": "Modules, pub and the crate as the build unit"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "`strlen` counts bytes, `toupper` misses `é`, and copying a 9-byte string into `char[8]` overflows the buffer.",
        "contrasts": [
            {"from": "Length is a scan to the NUL; capacity is fixed by the declaration.",
             "rust": "`String` stores its length and capacity and grows as needed."},
            {"from": "Bytes and characters are both `char`.",
             "rust": "`len()` counts UTF-8 bytes; `chars()` yields Unicode scalar values."},
            {"from": "`s[i]` reads byte `i`.",
             "rust": "`s[i]` does not compile; `&s[a..b]` must fall on character boundaries."},
        ],
        "credits": ["basics/strings", "basics/chars-and-text"],
    },
}

CHALLENGE = {
    "functions": ["truncate_at_boundary", "initials"],
    "source": r'''// C original:
// /* Cuts s to at most max bytes. May split a multi-byte character in half. */
// void truncate_bytes(char *s, size_t max) { if (strlen(s) > max) s[max] = '\0'; }
// /* Writes the first byte of each word, passed through toupper(). */
// void initials(const char *name, char *out) {
//     int start = 1;
//     for (; *name; name++) {
//         if (isspace((unsigned char)*name)) { start = 1; continue; }
//         if (start) *out++ = (char)toupper((unsigned char)*name);
//         start = 0;
//     }
//     *out = '\0';
// }
pub fn truncate_at_boundary(text: &str, max_bytes: usize) -> &str {
    todo!("implement the contract")
}

pub fn initials(name: &str) -> String {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;

fn main() {
    assert_eq!(solution::truncate_at_boundary("café", 4), "caf", "case 1");
    assert_eq!(solution::truncate_at_boundary("café", 5), "café", "case 2");
    assert_eq!(solution::truncate_at_boundary("café", 10), "café", "case 3");
    assert_eq!(solution::truncate_at_boundary("café", 0), "", "case 4");
    assert_eq!(solution::truncate_at_boundary("日本", 4), "日", "case 5");
    assert_eq!(solution::initials("ada lovelace"), "AL", "case 6");
    assert_eq!(solution::initials("élodie durand"), "ÉD", "case 7");
    assert_eq!(solution::initials("  grace   hopper "), "GH", "case 8");
    assert_eq!(solution::initials(""), "", "case 9");

    println!("PASS c-char-arrays-to-strings");
}
''',
    "cases": [
        ("boundary", 'solution::truncate_at_boundary("café", 4)', '"caf"'),
        ("visible", 'solution::truncate_at_boundary("café", 5)', '"café"'),
        ("boundary", 'solution::truncate_at_boundary("café", 10)', '"café"'),
        ("boundary", 'solution::truncate_at_boundary("café", 0)', '""'),
        ("semantic", 'solution::truncate_at_boundary("日本", 4)', '"日"'),
        ("visible", 'solution::initials("ada lovelace")', '"AL"'),
        ("semantic", 'solution::initials("élodie durand")', '"ÉD"'),
        ("boundary", 'solution::initials("  grace   hopper ")', '"GH"'),
        ("boundary", 'solution::initials("")', '""'),
    ],
}

EXPECT = {
    "example": "len=5 chars=4\nCAFÉ\nNone\nSome(\"caf\")\nMargaret Hamilton (17 bytes)\n0:c 1:a 2:f 3:é \n",
    "practice": {"errors": ["E0277"]},
    "recall": [{"panic": "byte index 4 is not a char boundary", "stdout": "None\n"}, None],
    "c": {"warnings": ["-Wfortify-source"], "sanitize": "address", "finding": "stack-buffer-overflow"},
    "wrong": {
        "c-char-arrays-to-strings.1.rs": {"mode": "panic", "note": "C habit: cut at the byte budget, `&text[..max_bytes]`, which splits `é`"},
        "c-char-arrays-to-strings.2.rs": {"mode": "panic", "note": "`to_ascii_uppercase`, the `toupper` equivalent, leaves `é` lowercase"},
    },
}
