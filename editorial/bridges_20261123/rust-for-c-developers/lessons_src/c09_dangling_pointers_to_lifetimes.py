ID = "c-dangling-pointers-to-lifetimes"
UNIT = "c-memory"
ORDER = 3

FROM_CODE = r'''#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Returns a pointer into a or b. Which one, and for how long, is up to the caller. */
static const char *longer(const char *a, const char *b) {
    return strlen(a) >= strlen(b) ? a : b;
}

int main(void) {
    char *a = strdup("short");
    char *b = strdup("much longer");
    const char *result = longer(a, b);
    free(b);                  /* ends b's storage; result still points into it */
    printf("%s\n", result);   /* ASan: heap-use-after-free */
    free(a);
    return 0;
}
'''

EXAMPLE = r'''// `'a`: the result borrows from `a` or `b`, so it is valid while both are.
fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() { a } else { b }
}

// One reference input: elision ties the result to `line`, no annotation needed.
fn first_word(line: &str) -> &str {
    line.split_whitespace().next().unwrap_or("")
}

fn main() {
    let a = String::from("short");
    {
        let b = String::from("much longer");
        let result = longer(&a, &b);
        println!("{result}"); // fine: b is still alive here
    }
    println!("{}", first_word("  hello world"));
}
'''

PRACTICE = r'''fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() { a } else { b }
}

fn main() {
    let a = String::from("short");
    let result;
    {
        let b = String::from("much longer");
        result = longer(&a, &b);
    }
    println!("{result}");
}
'''

LESSON = {
    "title": "Dangling Pointers and Lifetimes",
    "concept": "The compiler checks what the comment promised",
    "minutes": 13,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "A lifetime names how long a reference is valid, so the compiler rejects the dangling pointer that a C comment could only warn about.",
        "rule": "A lifetime annotation relates the output borrow to the input borrows; it never extends how long any value lives.",
        "explanation": (
            "A C function that returns a pointer into one of its arguments documents the relationship in a comment: the result points into `a` or `b`. The caller in the example frees `b` and then prints the result, and AddressSanitizer reports `heap-use-after-free`. Nothing in `const char *longer(const char *, const char *)` carries the fact that matters.\n\n"
            "Rust writes that fact into the signature. `fn longer<'a>(a: &'a str, b: &'a str) -> &'a str` says the result borrows from the inputs and may be used only while both borrows are valid. The compiler then checks every caller: using `result` after `b` has been dropped is error `E0597`, `b` does not live long enough.\n\n"
            "Most signatures need no annotation, because of elision. With exactly one reference input, the output borrows from it: `fn first_word(line: &str) -> &str`. With a `&self` method, the output borrows from `self`. With two reference inputs and a reference output there is no default, so rustc asks with `E0106`, missing lifetime specifier, because it cannot know which input you return.\n\n"
            "An annotation describes a relationship. It does not make anything live longer and cannot turn a dangling pointer into a valid one; returning a reference to a local, like `return buf;` for a stack array, is still rejected. Choose lifetimes that state what the code really does: if the result only ever points into `line`, only `line` should share `'a`. Tying `prefix` to it as well would force callers to keep `prefix` alive for no reason."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "`longer` needs `'a` because it has two reference inputs; `first_word` has one, so elision ties its result to `line`.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C functions, keeping the lifetimes in the starter: `after_prefix` returns the rest of `line` after `prefix`, or `None`, and borrows only from `line`; `longer` returns the input with more bytes, `a` on a tie.",
        "success": "The result of `after_prefix` stays usable after `prefix` is dropped, a line shorter than its prefix gives `None` instead of a panic, and a tie in `longer` returns `a`.",
        "question": "Why does `fn longer(a: &str, b: &str) -> &str` need a lifetime annotation when `fn first_word(line: &str) -> &str` does not?",
        "answers": [
            "With two reference inputs, the compiler cannot tell which one the result borrows from",
            "Functions that compare lengths always need annotations",
            "The annotation keeps `a` and `b` alive until the end of `main`",
            "A `&str` result always needs `'static`",
        ],
        "correctAnswer": 0,
        "feedback": "Elision covers one reference input, and `&self` methods. With two, you state the relationship; the annotation constrains callers and never extends a value's life.",
        "recall": [
            {
                "question": "Does annotating the return type as `&'static str` make this compile?",
                "code": "fn make() -> &'static str {\n    let s = String::from(\"temporary\");\n    &s\n}\n\nfn main() {\n    println!(\"{}\", make());\n}",
                "answer": "No. `'static` claims the text lives for the whole program, but `s` is dropped when `make` returns, so rustc rejects `&s` with `E0515`, cannot return a reference to a local variable. Return the `String` itself to hand over ownership.",
            },
            {
                "question": "Which inputs should share `'a` in a function that returns the part of `line` after `prefix`, and why does it matter to callers?",
                "answer": "Only `line`, because the result is part of `line` and never of `prefix`. `fn after_prefix<'a>(line: &'a str, prefix: &str) -> Option<&'a str>` lets a caller drop `prefix` and keep using the result; tying `prefix` to `'a` would force it to stay alive as long as the result.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Name the source", "detail": "For each returned reference, decide which input it points into; that input gets the output's lifetime."},
            {"title": "Leave the others free", "detail": "Inputs the result never points into keep their own, elided lifetime."},
            {"title": "Test a short-lived input", "detail": "Drop the unrelated input in an inner block and use the result afterwards; it must still compile."},
        ],
        "misconception": "“Adding `'a` makes the references live longer.”",
        "correction": "Lifetimes are checked, not executed. An annotation only describes which borrow the result depends on; if the data is dropped too early, the annotation makes the error precise rather than making the code valid.",
        "transferChallenge": "Write `struct Field<'a> { name: &'a str }` and a function that tries to build one from a `String` that goes out of scope first; read where rustc reports the error.",
        "connections": [
            {"direction": "previous", "title": "Pointer + Length to Slices", "concept": "A view that carries its own bounds"},
            {"direction": "next", "title": "Struct Copies: Copy and Clone", "concept": "Bitwise copies only for plain data"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "The result points into `b`; after `free(b)`, printing it is a heap use after free that AddressSanitizer reports.",
        "contrasts": [
            {"from": "Which argument a returned pointer refers to lives in a comment.",
             "rust": "The signature's lifetimes say it, and the compiler checks every caller."},
            {"from": "Freeing the source while a pointer into it remains compiles.",
             "rust": "Using a borrow after its source is dropped is error `E0597`."},
            {"from": "Returning the address of a local is only a warning.",
             "rust": "Returning a reference to a local is always an error."},
        ],
        "credits": ["ownership/lifetimes-intro"],
    },
}

CHALLENGE = {
    "functions": ["after_prefix", "longer"],
    "source": r'''// C original:
// /* Points just past `prefix` inside `line`, or NULL. Never points into `prefix`. */
// const char *after_prefix(const char *line, const char *prefix) {
//     size_t n = strlen(prefix);
//     return strncmp(line, prefix, n) == 0 ? line + n : NULL;
// }
// const char *longer(const char *a, const char *b) { return strlen(a) >= strlen(b) ? a : b; }
pub fn after_prefix<'a>(line: &'a str, prefix: &str) -> Option<&'a str> {
    todo!("implement the contract")
}

pub fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;

fn main() {
    let line = String::from("key=value");
    let rest = {
        let prefix = String::from("key=");
        solution::after_prefix(&line, &prefix)
    }; // prefix is gone; rest borrows only from line
    assert_eq!(rest, Some("value"), "case 1");
    assert_eq!(solution::after_prefix("key", "key="), None, "case 2");
    assert_eq!(solution::after_prefix("key=", "key="), Some(""), "case 3");
    assert_eq!(solution::after_prefix("café=1", "café="), Some("1"), "case 4");
    assert_eq!(solution::after_prefix("value", "key="), None, "case 5");
    assert_eq!(solution::longer("abc", "de"), "abc", "case 6");
    assert_eq!(solution::longer("ab", "cd"), "ab", "case 7: a tie returns a");
    assert_eq!(solution::longer("", "x"), "x", "case 8");

    println!("PASS c-dangling-pointers-to-lifetimes");
}
''',
    "cases": [
        ("visible", 'solution::after_prefix("key=value", "key=") with prefix dropped', 'Some("value")'),
        ("boundary", 'solution::after_prefix("key", "key=")', "None"),
        ("boundary", 'solution::after_prefix("key=", "key=")', 'Some("")'),
        ("semantic", 'solution::after_prefix("café=1", "café=")', 'Some("1")'),
        ("semantic", 'solution::after_prefix("value", "key=")', "None"),
        ("visible", 'solution::longer("abc", "de")', '"abc"'),
        ("boundary", 'solution::longer("ab", "cd")', '"ab"'),
        ("boundary", 'solution::longer("", "x")', '"x"'),
    ],
}

EXPECT = {
    "example": "much longer\nhello\n",
    "practice": {"errors": ["E0597"]},
    "recall": [{"errors": ["E0515"]}, None],
    "probes": {
        "elision": {"code": "fn longer(a: &str, b: &str) -> &str {\n    if a.len() >= b.len() { a } else { b }\n}\nfn main() {\n    println!(\"{}\", longer(\"a\", \"b\"));\n}", "errors": ["E0106"]},
    },
    "c": {"warnings": [], "sanitize": "address", "finding": "heap-use-after-free"},
    "wrong": {
        "c-dangling-pointers-to-lifetimes.1.rs": {"mode": "compile error E0597", "note": "ties `prefix` to `'a` as well, so the caller cannot drop `prefix` while using the result"},
        "c-dangling-pointers-to-lifetimes.2.rs": {"mode": "panic", "note": "C habit: skips past `prefix.len()` bytes without comparing, as with an unchecked `line + n`"},
    },
}
