ID = "c-printf-to-println"
UNIT = "c-syntax"
ORDER = 0

FROM_CODE = r'''#include <stdio.h>

int main(void) {
    const char *name = "bolt";
    unsigned qty = 7, code = 255;
    printf("%8s|%03u|%#06x\n", name, qty, code); /* "    bolt|007|0x00ff" */
    printf("%-8s|%u\n", name, qty);              /* "bolt    |7" */
    printf("%#x\n", 0u);                         /* "0": no prefix for zero */
    printf("%u items, %u left\n", qty);          /* only a -Wformat warning */
    return 0;
}
'''

EXAMPLE = r'''fn main() {
    let name = "bolt";
    let qty: u32 = 7;
    let code: u32 = 255;
    println!("{name:>8}|{qty:03}|{code:#06x}"); // "    bolt|007|0x00ff"
    println!("{name:8}|{qty}");                 // text pads on the right by default
    println!("{:#x}", 0);                       // "0x0": the prefix is always printed
    println!("{qty} items, {} left", qty - 2);  // every placeholder needs a value
    eprintln!("debug: {:?}", (name, qty));      // stderr, Debug formatting
    let line = format!("{name}={qty}");         // same checks, returns a String
    println!("{line}");
}
'''

PRACTICE = r'''fn main() {
    let qty = 7;
    println!("{} items, {} left", qty);
}
'''

LESSON = {
    "title": "From printf to println!",
    "concept": "Format strings checked at compile time",
    "minutes": 9,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "`println!` checks its format string against its arguments while compiling; `printf` trusts you until run time.",
        "rule": "`println!` is a macro: placeholders and arguments are matched during compilation, so a missing or mistyped argument is a compile error, not undefined behaviour.",
        "explanation": (
            "`printf` is an ordinary variadic function. The compiler passes whatever arguments you wrote, and the C library reads them back according to the format string at run time. Clang and GCC compare the two as a courtesy (`-Wformat`), but a mismatch is still valid C with undefined behaviour: the second `%u` in the example reads an argument that was never passed.\n\n"
            "`println!`, `print!`, `eprintln!` and `format!` are macros, which is what the `!` means. They expand during compilation, so rustc sees the format string and every argument together. One placeholder too many is a compile error. Each value must also implement the trait its placeholder asks for: `Display` for `{}`, `Debug` for `{:?}`, `LowerHex` for `{:x}`. There are no length modifiers such as `%ld` or `%zu`, because the argument's type already says how wide it is.\n\n"
            "The flags map closely: `{:>8}` is `%8s`, `{:03}` is `%03u`, `{:#06x}` is `%#06x` and `{:.2}` is `%.2f`. Two defaults differ. A bare width pads text on the right (`{:8}` behaves like `%-8s`) while numbers still pad on the left, and `#` always prints the `0x` prefix, even for zero, where C prints plain `0`. A variable in scope can be named inside the braces, as in `{qty}`.\n\n"
            "Execution still starts in `fn main()`. `println!` writes a line to stdout and `eprintln!` to stderr. `format!` returns the text as an owned `String` instead of filling a caller-sized buffer, so there is no `snprintf` truncation to check."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "The same lines as the C program, plus `eprintln!` for stderr and `format!`, which returns a `String` instead of writing into a buffer.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C `snprintf` call: `label` returns the name right-aligned in 8 columns, the quantity zero-padded to 3 digits and the code as `0x`-prefixed hex zero-padded to width 6, separated by `|`. Keep Rust's prefix for zero (`0x0000`).",
        "success": "`label(\"bolt\", 7, 255)` returns `    bolt|007|0x00ff`, longer names are never cut, and a zero code prints as `0x0000`.",
        "question": "The practice program has two `{}` placeholders and one argument. What happens?",
        "answers": [
            "It prints `7 items,  left` and continues",
            "It compiles with a warning, like `-Wformat`",
            "rustc rejects it while expanding the macro, before any code runs",
            "It panics at run time when it reaches the second placeholder",
        ],
        "correctAnswer": 2,
        "feedback": "`println!` is expanded during compilation, so rustc counts placeholders against arguments and stops with `2 positional arguments in format string, but there is 1 argument`.",
        "recall": [
            {
                "question": "Why does `{:8}` give a different result for `\"bolt\"` than `%8s` does in C?",
                "answer": "Rust pads non-numeric values on the right by default, so `{:8}` gives `bolt    `, like `%-8s`. Numbers still pad on the left. Write `{:>8}` to right-align text the way `%8s` does.",
            },
            {
                "question": "What do these two lines print?",
                "code": "println!(\"{:#x}\", 0);\nprintln!(\"{:#06x}\", 255);",
                "answer": "`0x0` and `0x00ff`. With `#`, Rust always prints the `0x` prefix, even for zero, and the width counts the prefix. C's `%#x` prints plain `0` for zero.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Match the flags", "detail": "Pair each C conversion with its Rust placeholder: `%8s` becomes `{:>8}`, `%03u` becomes `{:03}`, `%#06x` becomes `{:#06x}`."},
            {"title": "Check the defaults", "detail": "Look for bare widths on text and `#` on values that may be zero; those are the two places a literal translation changes the output."},
            {"title": "Let rustc count", "detail": "Remove one argument from a `println!` and read the error: the format string is checked as part of compilation."},
        ],
        "misconception": "“`println!` is Rust's `printf`, so a wrong argument shows up as garbage output.”",
        "correction": "`println!` is a macro that rustc expands and type-checks. A missing argument, an extra argument or a value without the requested trait (for example `{}` on a type without `Display`) stops the build. Garbage output from a mismatched format is not possible in safe Rust.",
        "transferChallenge": "Print a `u64` byte count with `{:>12}` and the same value with `{:e}`. Then try `{:x}` on an `f64` and read which trait rustc says is missing.",
        "connections": [
            {"direction": "next", "title": "const by Default", "concept": "Immutable bindings, mut and shadowing"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "Correct output for matching arguments; the last call compiles with only a `-Wformat` warning and reads an argument that was never passed.",
        "contrasts": [
            {"from": "`printf` checks nothing itself; `-Wformat` is an optional compiler warning.",
             "rust": "`println!` expands at compile time; a missing argument is a compile error."},
            {"from": "`%ld`, `%zu` and `%u` must match each argument's exact type.",
             "rust": "The argument's type decides; the placeholder picks a trait: `{}`, `{:?}`, `{:x}`."},
            {"from": "`%8s` right-aligns text; `%#x` prints `0` for zero.",
             "rust": "`{:8}` left-aligns text; `{:#x}` prints `0x0`."},
            {"from": "`snprintf` truncates into a buffer the caller must size.",
             "rust": "`format!` returns an owned `String` that grows as needed."},
        ],
        "credits": ["basics/hello-rust", "basics/print-formatting"],
    },
}

CHALLENGE = {
    "functions": ["label"],
    "source": r'''// C original:
// /* buf must hold the whole label, or snprintf silently truncates it. */
// void label(char *buf, size_t n, const char *name, unsigned qty, unsigned code) {
//     snprintf(buf, n, "%8s|%03u|%#06x", name, qty, code);
// }
pub fn label(name: &str, qty: u32, code: u32) -> String {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;

fn main() {
    assert_eq!(solution::label("bolt", 7, 255), "    bolt|007|0x00ff", "case 1");
    assert_eq!(solution::label("hexagon-nut", 1200, 4096), "hexagon-nut|1200|0x1000", "case 2");
    assert_eq!(solution::label("", 0, 0), "        |000|0x0000", "case 3");
    assert_eq!(solution::label("nut", 42, 0xabcdef), "     nut|042|0xabcdef", "case 4");

    println!("PASS c-printf-to-println");
}
''',
    "cases": [
        ("visible", 'solution::label("bolt", 7, 255)', '"    bolt|007|0x00ff"'),
        ("boundary", 'solution::label("hexagon-nut", 1200, 4096)', '"hexagon-nut|1200|0x1000"'),
        ("boundary", 'solution::label("", 0, 0)', '"        |000|0x0000"'),
        ("semantic", 'solution::label("nut", 42, 0xabcdef)', '"     nut|042|0xabcdef"'),
    ],
}

EXPECT = {
    "example": "    bolt|007|0x00ff\nbolt    |7\n0x0\n7 items, 5 left\nbolt=7\n",
    "practice": {"message": "2 positional arguments in format string, but there is 1 argument"},
    "recall": [None, {"stdout": "0x0\n0x00ff\n"}],
    "c": {"warnings": ["-Wformat-insufficient-args"], "stdoutPrefix": "    bolt|007|0x00ff\nbolt    |7\n0\n", "exit": 0},
    "wrong": {
        "c-printf-to-println.1.rs": {"mode": "panic", "note": "C habit: `{name:8}` for `%8s` left-aligns the name"},
    },
}
