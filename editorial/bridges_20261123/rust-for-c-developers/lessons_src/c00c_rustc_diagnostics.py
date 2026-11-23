ID = "c-rustc-diagnostics"
UNIT = "c-rust-at-a-glance"
ORDER = 2

FROM_CODE = r'''#include <stdio.h>
#include <stdlib.h>

/* Sums the readings and frees them: the caller must not touch them again. */
static int total(int *values, int n) {
    int sum = 0;
    for (int i = 0; i < n; i++) sum += values[i];
    free(values);
    return sum;
}

int main(int argc, char **argv) {
    (void)argv;
    int *readings = malloc(3 * sizeof *readings);
    if (!readings) return 1;
    readings[0] = 3; readings[1] = 4; readings[2] = 5;
    int count;
    if (argc > 0) count = 3;            /* -Wall: may be used uninitialized */
    int sum = total(readings, count);
    printf("%d from %d, first %d\n", sum, count, readings[0]); /* no warning */
    return 0;
}
'''

EXAMPLE = r'''// The fix the diagnostic's note points to: borrow instead of taking ownership.
fn total(values: &[i32]) -> i32 {
    values.iter().sum()
}

fn main() {
    let readings = vec![3, 4, 5];
    let sum = total(&readings);
    println!("{sum} from {} readings, first {}", readings.len(), readings[0]);
}
'''

PRACTICE = r'''fn total(values: Vec<i32>) -> i32 {
    values.iter().sum()
}

fn main() {
    let readings = vec![3, 4, 5];
    let sum = total(readings);
    println!("{sum} from {} readings", readings.len());
}
'''

LESSON = {
    "title": "Reading rustc Diagnostics",
    "concept": "Compile-time errors instead of run-time crashes",
    "minutes": 11,
    "exerciseKind": "planned",
    "writing": {
        "summary": "Where a C program compiles and crashes later, rustc stops with an error code, the exact spans involved and a suggested fix; reading them in order is a skill worth learning first.",
        "rule": "Repair the first causal error before chasing its downstream messages: read its code and primary span, then the labels, notes and help, fix the cause and recompile.",
        "explanation": (
            "In C the compiler's main job is translation, and whole classes of bugs produce no diagnostic at all. The example's use after free compiles silently even with `-Wall -Wextra`; the only warning is about `count`, which may be used uninitialised. `-Werror` turns that warning into a build failure, and the use after free surfaces only at run time, as `heap-use-after-free` under AddressSanitizer.\n\n"
            "rustc refuses the equivalent program instead, and its diagnostic has a fixed anatomy. The first line gives the severity, the error code and the rule: `error[E0382]: borrow of moved value`. The `-->` line gives the file, line and column. Under the source, `^^^` marks the primary span, the place where the rule is broken (`value borrowed here after move`), and `---` marks secondary spans that explain why: where the value moved, and that `Vec<i32>` does not implement `Copy`. `note:` lines add context, here pointing at the parameter that takes ownership, and `help:` lines propose a change.\n\n"
            "Read in that order and fix the first error first. One root mistake can produce several later errors, so recompile after each fix before reading the rest. Treat `help:` as evidence, not a command: `consider cloning the value` would compile, but the note's suggestion to borrow, `values: &[i32]`, matches what the program means and copies nothing. For any code, `rustc --explain E0382` prints the rule with examples, offline.\n\n"
            "Errors and warnings are separate in Rust. An error, such as a move, a type mismatch or a possibly uninitialised read (`E0381`), means no program is built; there is no flag that lets it through. Lints such as unused variables are warnings by default, and `#![deny(warnings)]` in the crate, or `RUSTFLAGS=\"-D warnings\"` in CI, is the equivalent of `-Werror`. `cargo clippy` adds further lints, much as extra `-W` flags do for clang."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "Following the note rather than the `clone` help: `total` borrows a slice, so `readings` is still usable afterwards.",
        "practiceCode": PRACTICE,
        "task": "Compile the practice program, label each part of the diagnostic (code, primary span, secondary spans, note, help), then choose between the `clone` help and the borrowing note.",
        "success": "You can point to the `^^^` span that breaks the rule, the `---` span that explains it, and explain why borrowing is a better fix than cloning here.",
        "question": "After one edit, rustc reports three errors: `E0308` at a call to `total`, then two more in later lines that use its result. What do you do first?",
        "answers": [
            "Fix the first error at its primary span, recompile, and then see which later errors remain",
            "Fix the last error first, because it is closest to the end of `main`",
            "Apply every `help:` suggestion in the order printed",
            "Silence the errors with `#[allow(...)]` attributes",
        ],
        "correctAnswer": 0,
        "feedback": "Later errors are often consequences of the first. Its primary span shows where the rule breaks; fix that cause, rebuild, and only then read what is left.",
        "recall": [
            {
                "question": "In a rustc diagnostic, what do the `^^^` and `---` markers under the source mean?",
                "answer": "`^^^` marks the primary span, the place where the rule is broken, with the main label (for example `value borrowed here after move`). `---` marks secondary spans that explain why, such as `value moved here`. Read the primary span first, then the labels.",
            },
            {
                "question": "Does this compile? What plays the role of `gcc -Wall -Werror` here?",
                "code": "#![deny(warnings)]\n\nfn main() {\n    let unused = 5;\n    println!(\"ok\");\n}",
                "answer": "No. Warnings are on by default, and `#![deny(warnings)]`, or `RUSTFLAGS=\"-D warnings\"` in CI, turns them into errors, so the unused variable stops the build. Errors such as `E0382` were never optional in the first place.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Read the header", "detail": "Note the severity, the error code and the one-line rule, such as `error[E0382]: borrow of moved value`."},
            {"title": "Follow the spans", "detail": "Start at `^^^`, then read each `---` label to see where the value came from and why the rule applies."},
            {"title": "Weigh the help", "detail": "Compare each `help:` and `note:` with what the program should mean; choose the fix you can explain, then recompile."},
        ],
        "misconception": "“The `help:` line is the fix; apply it and move on.”",
        "correction": "A `help:` line is one change that would compile. It may cost a copy (`clone`) or turn a compile error into a run-time panic (`unwrap`). Decide what the program should mean first; the notes often point to a better fix.",
        "transferChallenge": "Run `rustc --explain E0502` and `rustc --explain E0308`, then write a two-line program that triggers each and match its spans to the explanation.",
        "connections": [
            {"direction": "previous", "title": "What Safe Rust Rules Out", "concept": "Undefined behaviour excluded, bugs still possible"},
            {"direction": "next", "title": "From printf to println!", "concept": "Format strings checked at compile time"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "`-Wall` warns only about `count`; the use after free compiles silently and is found at run time by AddressSanitizer.",
        "contrasts": [
            {"from": "A use after free compiles without a diagnostic, even with `-Wall -Wextra`.",
             "rust": "A use after move is error `E0382`, with spans for where the value moved and where it was used."},
            {"from": "`-Wall` warns about a possibly uninitialised variable; `-Werror` makes it fatal.",
             "rust": "Reading a possibly uninitialised binding is always error `E0381`."},
            {"from": "Warning flags are looked up in the compiler manual.",
             "rust": "`rustc --explain E0382` prints the rule with examples, offline."},
            {"from": "`-Werror` promotes warnings to errors.",
             "rust": "`#![deny(warnings)]` or `-D warnings` does the same for rustc lints."},
        ],
        "credits": ["basics/compiler-feedback"],
    },
}

EXPECT = {
    "example": "12 from 3 readings, first 3\n",
    "practice": {"errors": ["E0382"], "messages": [
        "borrow of moved value: `readings`",
        "^^^^^^^^ value borrowed here after move",
        "-------- value moved here",
        "which does not implement the `Copy` trait",
        "note: consider changing this parameter type in function `total` to borrow instead",
        "help: consider cloning the value",
        "For more information about this error, try `rustc --explain E0382`.",
    ]},
    "recall": [None, {"message": "unused variable: `unused`"}],
    "probes": {
        "uninitialised-is-an-error": {"code": "let count: i32;\nif std::env::args().count() > 0 {\n    count = 3;\n}\nprintln!(\"{count}\");", "errors": ["E0381"]},
        "warning-does-not-stop-the-build": {"code": "fn main() {\n    let unused = 5;\n    println!(\"ok\");\n}", "stdout": "ok\n"},
    },
    "explain": ("E0382", "A variable was used after its contents have been moved elsewhere."),
    "c": {"warnings": ["-Wsometimes-uninitialized"], "werror": "-Wsometimes-uninitialized",
          "stdoutPrefix": "12 from 3, first ", "exit": 0,
          "sanitize": "address", "finding": "heap-use-after-free"},
}
