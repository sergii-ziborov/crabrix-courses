ID = "c-functions-are-expressions"
UNIT = "c-syntax"
ORDER = 3

FROM_CODE = r'''#include <stdio.h>

static int clamp(int v, int lo, int hi) {
    return v < lo ? lo : v > hi ? hi : v;   /* nested ternary */
}

static int sign(int x) {
    if (x > 0) return 1;                     /* `if` is a statement */
    if (x < 0) return -1;
    return 0;
}

static int is_even(int x) { return !(x % 2); } /* an int stands in for bool */

int main(void) {
    printf("%d %d %d\n", clamp(-5, 0, 10), clamp(7, 0, 10), clamp(42, 0, 10));
    printf("%d %d %d\n", sign(-3), sign(0), sign(9));
    if (is_even(4)) printf("4 is even\n");
    return 0;
}
'''

EXAMPLE = r'''fn clamp(v: i32, lo: i32, hi: i32) -> i32 {
    if v < lo { lo } else if v > hi { hi } else { v } // the whole `if` is the value
}

fn sign(x: i32) -> i32 {
    if x > 0 {
        return 1; // an early `return` still exists
    }
    if x < 0 { -1 } else { 0 }
}

fn is_even(x: i32) -> bool {
    x % 2 == 0 // tail expression, no semicolon: the return value
}

fn main() {
    println!("{} {} {}", clamp(-5, 0, 10), clamp(7, 0, 10), clamp(42, 0, 10));
    println!("{} {} {}", sign(-3), sign(0), sign(9));
    if is_even(4) {
        println!("4 is even");
    }
}
'''

PRACTICE = r'''fn days(leap: bool) -> u32 {
    if leap { 29 } else { 28 };
}

fn main() {
    println!("{}", days(true));
}
'''

LESSON = {
    "title": "Functions Are Expressions",
    "concept": "Tail values replace return and the ternary",
    "minutes": 10,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "A Rust block evaluates to its last expression, so functions return without `return`, and `if` replaces the ternary operator.",
        "rule": "A block's value is its final expression without a semicolon; adding the semicolon turns it into a statement, and the block evaluates to `()`.",
        "explanation": (
            "C separates statements from expressions: `if` is a statement, so choosing a value needs `?:`, and a function hands back a value only through `return`. In Rust almost everything is an expression. A block `{ ... }` evaluates to its last expression, and a function body is a block, so `fn is_even(x: i32) -> bool` can end with the comparison itself. `return` still exists for early exits.\n\n"
            "`if` is an expression too, which is why Rust has no ternary operator: `if v < lo { lo } else { v }` is the value. Both branches must have the same type, and the condition must be a `bool`. C's habit of testing an integer, `if (flags & MASK)`, is a type error; write `flags & MASK != 0`. Unlike C, `&` binds tighter than `!=` in Rust, so that expression means what it says.\n\n"
            "The semicolon is significant. `x + 1` at the end of a block is the block's value; `x + 1;` is a statement that discards it, and the block then evaluates to `()`, the unit type. In a function that promises `u32`, that is error `E0308`, and rustc's help points at the semicolon to remove. Read semicolons this way and the rule becomes mechanical.\n\n"
            "Parameters need full types, and arguments are never converted to fit them: passing an `i32` where a `u32` is expected does not compile. There are no prototypes and no forward declarations; functions in a module can be defined in any order."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "`clamp` is one `if` expression, `sign` mixes an early `return` with a tail `if`, and `is_even` ends with its comparison.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C functions: `is_leap` applies the Gregorian rule (divisible by 4, except centuries, except every 400th year) and `days_in_february` returns 29 or 28.",
        "success": "2024 and 2000 are leap years, 1900 and 2023 are not, and February has 29 days only in leap years.",
        "question": "Why does rustc reject `fn days(leap: bool) -> u32 { if leap { 29 } else { 28 }; }`?",
        "answers": [
            "`if` cannot produce a value; use a `match`",
            "The function is missing `return`",
            "`29` and `28` are `i32`, not `u32`",
            "The semicolon makes the `if` a statement, so the body evaluates to `()`",
        ],
        "correctAnswer": 3,
        "feedback": "Remove the semicolon and the `if` expression becomes the body's value. The literals take the type `u32` from the signature.",
        "recall": [
            {
                "question": "What does this print?",
                "code": "let value = {\n    let x = 2;\n    x * 3;\n};\nprintln!(\"{value:?}\");",
                "answer": "`()`. The semicolon after `x * 3` discards the product, so the block has no tail expression and evaluates to the unit value.",
            },
            {
                "question": "In C, `flags & MASK == 0` is a classic precedence bug. What does this Rust version print?",
                "code": "const MASK: u8 = 0b100;\nlet flags: u8 = 0b110;\nprintln!(\"{}\", flags & MASK == 0);",
                "answer": "`false`. In C, `==` binds tighter than `&`, so the expression computes `flags & (MASK == 0)`. In Rust, `&` binds tighter than comparisons, so this is `(flags & MASK) == 0`, a `bool` that `if` accepts.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Find the tail", "detail": "In each block, locate the last expression and check whether a semicolon follows it."},
            {"title": "Type both branches", "detail": "For every `if` used as a value, confirm that both branches produce the same type."},
            {"title": "Replace integer tests", "detail": "Rewrite C conditions such as `if (n)` as explicit comparisons such as `n != 0`."},
        ],
        "misconception": "“A Rust function without `return` hands back whatever is left over, like falling off the end of a C function.”",
        "correction": "Using the result of a non-`void` C function that falls off its end is undefined. In Rust the end of the body is the return value; if that value is `()` but the signature promises another type, the program does not compile.",
        "transferChallenge": "Write `fn sign(x: i32) -> i32` as a single `if`/`else if`/`else` expression, then add a semicolon after it and read rustc's help line.",
        "connections": [
            {"direction": "previous", "title": "Integer Overflow and Casts", "concept": "Defined overflow policy and explicit conversions"},
            {"direction": "next", "title": "From for(;;) to Ranges", "concept": "Ranges, iterators and loop with a value"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "C needs `return`, a nested ternary and an `int` that stands in for a boolean.",
        "contrasts": [
            {"from": "A value comes back only through `return`.",
             "rust": "A body's last expression without `;` is the return value."},
            {"from": "`cond ? a : b`, because `if` is a statement.",
             "rust": "`if cond { a } else { b }` is an expression; both branches share one type."},
            {"from": "Any non-zero integer is true in a condition.",
             "rust": "A condition must be a `bool`; `if n` with an integer is `E0308`."},
        ],
        "credits": ["basics/functions", "basics/block-expressions"],
    },
}

CHALLENGE = {
    "functions": ["is_leap", "days_in_february"],
    "source": r'''// C original:
// int is_leap(int year) { return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0; }
// int days_in_february(int year) { return is_leap(year) ? 29 : 28; }
pub fn is_leap(year: i32) -> bool {
    todo!("implement the contract")
}

pub fn days_in_february(year: i32) -> u32 {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;

fn main() {
    assert!(solution::is_leap(2024), "case 1");
    assert!(!solution::is_leap(1900), "case 2");
    assert!(solution::is_leap(2000), "case 3");
    assert!(!solution::is_leap(2023), "case 4");
    assert_eq!(solution::days_in_february(2024), 29, "case 5");
    assert_eq!(solution::days_in_february(1900), 28, "case 6");

    println!("PASS c-functions-are-expressions");
}
''',
    "cases": [
        ("visible", "solution::is_leap(2024)", "true"),
        ("boundary", "solution::is_leap(1900)", "false"),
        ("boundary", "solution::is_leap(2000)", "true"),
        ("visible", "solution::is_leap(2023)", "false"),
        ("semantic", "solution::days_in_february(2024)", "29"),
        ("semantic", "solution::days_in_february(1900)", "28"),
    ],
}

EXPECT = {
    "example": "0 7 10\n-1 0 1\n4 is even\n",
    "practice": {"errors": ["E0308"]},
    "recall": [{"stdout": "()\n"}, {"stdout": "false\n"}],
    "probes": {
        "quiz-fixed": {"code": "fn days(leap: bool) -> u32 {\n    if leap { 29 } else { 28 }\n}\nfn main() {\n    println!(\"{} {}\", days(true), days(false));\n}", "stdout": "29 28\n"},
        "integer-condition": {"code": "let n = 3;\nif n { println!(\"yes\"); }", "errors": ["E0308"]},
    },
    "c": {"warnings": [], "stdout": "0 7 10\n-1 0 1\n4 is even\n", "exit": 0},
    "wrong": {
        "c-functions-are-expressions.1.rs": {"mode": "panic", "note": "only `year % 4 == 0`: 1900 counted as a leap year"},
        "c-functions-are-expressions.2.rs": {"mode": "compile error E0308", "note": "C-style trailing semicolon after the tail expression"},
    },
}
