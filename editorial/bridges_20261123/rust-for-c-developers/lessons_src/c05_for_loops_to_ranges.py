ID = "c-for-loops-to-ranges"
UNIT = "c-syntax"
ORDER = 4

FROM_CODE = r'''#include <stdio.h>

int main(void) {
    int xs[] = {4, 8, 15, 16, 23, 42};
    size_t n = sizeof xs / sizeof xs[0];
    int sum = 0;
    for (size_t i = 0; i < n; i++) sum += xs[i];      /* an index you manage */
    int total = 0;
    for (int i = 1; i <= 10; i++) total += i;          /* inclusive bound */
    for (size_t i = n; i-- > 0;) printf("%d ", xs[i]); /* reverse without underflow */
    printf("\nsum=%d total=%d\n", sum, total);
    size_t first_big = n;                               /* sentinel: not found */
    for (size_t i = 0; i < n; i++)
        if (xs[i] > 20) { first_big = i; break; }
    printf("first_big=%zu\n", first_big);
    return 0;
}
'''

EXAMPLE = r'''fn main() {
    let xs = [4, 8, 15, 16, 23, 42];
    let mut sum = 0;
    for x in xs {               // values, not indices
        sum += x;
    }
    let mut total = 0;
    for i in 1..=10 {           // `..=` includes 10; `1..10` stops at 9
        total += i;
    }
    for x in xs.iter().rev() {  // no unsigned-underflow idiom needed
        print!("{x} ");
    }
    println!("\nsum={sum} total={total}");
    let mut i = 0;
    let first_big = loop {      // `break value` replaces the sentinel
        if i == xs.len() { break None; }
        if xs[i] > 20 { break Some(i); }
        i += 1;
    };
    println!("first_big={first_big:?}");
}
'''

PRACTICE = r'''fn main() {
    let xs = [4, 8, 15];
    let mut i = xs.len() - 1;
    while i >= 0 {
        print!("{} ", xs[i]);
        i -= 1;
    }
}
'''

LESSON = {
    "title": "From for(;;) to Ranges",
    "concept": "Ranges, iterators and loop with a value",
    "minutes": 11,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "`for` iterates over ranges and collections, `..=` includes the end safely, and `loop` can hand a value out with `break`.",
        "rule": "`for` iterates over a range or collection; `a..b` excludes `b`, `a..=b` includes it, and `loop` with `break value` replaces sentinel variables.",
        "explanation": (
            "Rust has no `for (init; cond; step)`. `for` takes anything iterable: a range such as `0..n`, an array, a `Vec` or an iterator chain. The loop variable is a fresh binding in each iteration, and the range is built once before the loop starts. `for x in xs` visits values directly, so there is no index to get wrong; when you need the index as well, `for (i, x) in xs.iter().enumerate()` gives both.\n\n"
            "`a..b` is half-open, like `i < b`; `a..=b` is closed, like `i <= b`. The inclusive form matters at type limits. In C, `for (unsigned char i = lo; i <= hi; i++)` never ends when `hi` is 255, because `i` wraps to 0. A Rust port written as `lo..hi + 1` panics in a debug build when `hi + 1` overflows. `lo..=hi` visits 255 and stops, because the range records that it has produced its last element instead of computing `hi + 1`.\n\n"
            "Reverse iteration is `.rev()`, which replaces the `for (size_t i = n; i-- > 0;)` idiom that avoids an unsigned underflow. `while cond { }` works as in C. `loop { }` is an unconditional loop, and it is an expression: `break value` ends it and becomes its value, which replaces the sentinel pattern where `first_big = n` means not found.\n\n"
            "Labels such as `'outer: for ...` with `break 'outer` replace a `goto` out of nested loops. Most index searches also have iterator methods (`position`, `find`, `any`), but a clear `for` or `loop` is equally idiomatic when it reads better."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "Values instead of indices, an inclusive range, `.rev()` instead of the underflow idiom, and a `loop` whose `break` yields `Some(4)` or `None`.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C functions: `count_multiples` counts the multiples of `k` in `lo..=hi` (zero when `lo > hi`, and `k` is at least 1), and `first_power_at_least` returns the smallest power of two that is at least `n` (1 for 0 and 1; `n` is at most 2^31).",
        "success": "`count_multiples(250, 255, 5)` is 2 without overflow, `count_multiples(7, 3, 2)` is 0, and `first_power_at_least(5)` is 8.",
        "question": "What is `total` after `let mut n = 1; let found = loop { if n * n > 20 { break n; } n += 1; }; let total: u32 = (found..=7).sum();`?",
        "answers": [
            "18",
            "11",
            "13",
            "It does not compile: `loop` has no value",
        ],
        "correctAnswer": 0,
        "feedback": "`loop` ends with `break n` when `n` is 5, so `found` is 5, and `5..=7` includes 7: 5 + 6 + 7 = 18.",
        "recall": [
            {
                "question": "Why does `for i in 0..=u8::MAX` terminate while the C loop `for (unsigned char i = 0; i <= 255; i++)` does not?",
                "answer": "The C counter wraps from 255 to 0, so `i <= 255` is always true. A Rust `RangeInclusive` records when it has yielded its last element, so it produces 0 through 255 and then stops without ever computing 256.",
            },
            {
                "question": "What does this print?",
                "code": "let xs = [3, 1, 4, 1, 5];\nlet mut i = 0;\nlet at = loop {\n    if i == xs.len() { break None; }\n    if xs[i] == 4 { break Some(i); }\n    i += 1;\n};\nprintln!(\"{at:?} {:?}\", xs.iter().position(|&x| x == 9));",
                "answer": "`Some(2) None`. The `loop` breaks with `Some(2)` at the first 4, and `position` runs the same kind of search with an iterator and finds no 9.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Classify each loop", "detail": "Over a collection: `for x in xs`. Over numbers: a range. Until a condition with a result: `loop` with `break value`."},
            {"title": "Check the end bound", "detail": "Translate `<` to `..` and `<=` to `..=`; never write `hi + 1` on a type that can be at its maximum."},
            {"title": "Remove the sentinels", "detail": "Replace not-found markers such as `n` or `-1` with a `break` that yields an `Option`."},
        ],
        "misconception": "“`a..=b` is just `a..b + 1` written differently.”",
        "correction": "`a..b + 1` computes `b + 1`, which overflows when `b` is the type's maximum: a panic in debug builds and an empty range in release builds. `a..=b` never computes `b + 1`.",
        "transferChallenge": "Rewrite the practice program with `for x in xs.iter().rev()`, then with a labelled loop over two arrays that stops at the first pair whose sum is above 20.",
        "connections": [
            {"direction": "previous", "title": "Functions Are Expressions", "concept": "Tail values replace return and the ternary"},
            {"direction": "next", "title": "From malloc/free to Ownership", "concept": "One owner frees, exactly once"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "Index loops, an inclusive bound, the `i-- > 0` reverse idiom and a sentinel value that means not found.",
        "contrasts": [
            {"from": "`for (i = 0; i < n; i++)` with an index you manage.",
             "rust": "`for x in xs` or `for i in 0..n`; the loop variable is a new binding each time."},
            {"from": "`i <= hi` never ends when `hi` is the type's maximum.",
             "rust": "`lo..=hi` includes `hi` and terminates, even at `u8::MAX`."},
            {"from": "A sentinel such as `n` means not found.",
             "rust": "`loop { ... break Some(i) ... }` returns the result directly."},
        ],
        "credits": ["basics/loops", "basics/ranges"],
    },
}

CHALLENGE = {
    "functions": ["count_multiples", "first_power_at_least"],
    "source": r'''// C original:
// unsigned count_multiples(unsigned char lo, unsigned char hi, unsigned char k) {
//     unsigned count = 0;
//     for (int i = lo; i <= hi; i++)   /* an int counter, so hi == 255 terminates */
//         if (i % k == 0) count++;
//     return count;
// }
// unsigned first_power_at_least(unsigned n) {
//     unsigned p = 1;
//     while (p < n) p *= 2;
//     return p;
// }
pub fn count_multiples(lo: u8, hi: u8, k: u8) -> u32 {
    todo!("implement the contract")
}

pub fn first_power_at_least(n: u32) -> u32 {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;

fn main() {
    assert_eq!(solution::count_multiples(1, 10, 3), 3, "case 1");
    assert_eq!(solution::count_multiples(250, 255, 5), 2, "case 2");
    assert_eq!(solution::count_multiples(0, 255, 1), 256, "case 3");
    assert_eq!(solution::count_multiples(7, 3, 2), 0, "case 4");
    assert_eq!(solution::first_power_at_least(0), 1, "case 5");
    assert_eq!(solution::first_power_at_least(5), 8, "case 6");
    assert_eq!(solution::first_power_at_least(64), 64, "case 7");
    assert_eq!(solution::first_power_at_least(1 << 31), 1 << 31, "case 8");

    println!("PASS c-for-loops-to-ranges");
}
''',
    "cases": [
        ("visible", "solution::count_multiples(1, 10, 3)", "3"),
        ("boundary", "solution::count_multiples(250, 255, 5)", "2"),
        ("boundary", "solution::count_multiples(0, 255, 1)", "256"),
        ("semantic", "solution::count_multiples(7, 3, 2)", "0"),
        ("boundary", "solution::first_power_at_least(0)", "1"),
        ("visible", "solution::first_power_at_least(5)", "8"),
        ("semantic", "solution::first_power_at_least(64)", "64"),
        ("boundary", "solution::first_power_at_least(1 << 31)", "1 << 31"),
    ],
}

EXPECT = {
    "example": "42 23 16 15 8 4 \nsum=108 total=55\nfirst_big=Some(4)\n",
    "practice": {"panic": "attempt to subtract with overflow", "stdout": "15 8 4 "},
    "recall": [None, {"stdout": "Some(2) None\n"}],
    "probes": {
        "quiz": {"code": "let mut n = 1;\nlet found = loop {\n    if n * n > 20 { break n; }\n    n += 1;\n};\nlet total: u32 = (found..=7).sum();\nprintln!(\"{total}\");", "stdout": "18\n"},
        "inclusive-at-max": {"code": "let mut count = 0u32;\nfor _ in 0..=u8::MAX { count += 1; }\nprintln!(\"{count}\");", "stdout": "256\n"},
    },
    "c": {"warnings": [], "stdout": "42 23 16 15 8 4 \nsum=108 total=55\nfirst_big=4\n", "exit": 0},
    "wrong": {
        "c-for-loops-to-ranges.1.rs": {"mode": "panic", "note": "`lo..hi + 1` overflows at 255: a panic in debug builds, an empty range in release builds"},
        "c-for-loops-to-ranges.2.rs": {"mode": "panic", "note": "`lo..hi` translates `<=` as `<` and misses the last value"},
    },
}
