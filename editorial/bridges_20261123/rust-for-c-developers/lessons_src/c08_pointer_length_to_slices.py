ID = "c-pointer-length-to-slices"
UNIT = "c-memory"
ORDER = 2

FROM_CODE = r'''#include <stdio.h>

static int max_in(const int xs[], size_t n) {  /* xs is really const int * */
    printf("sizeof xs = %zu\n", sizeof xs);      /* pointer size, not the array */
    int best = xs[0];
    for (size_t i = 1; i <= n; i++)              /* off by one: reads xs[n] */
        if (xs[i] > best) best = xs[i];
    return best;
}

int main(void) {
    int xs[] = {4, 9, 2};
    printf("max = %d\n", max_in(xs, sizeof xs / sizeof xs[0]));
    return 0;
}
'''

EXAMPLE = r'''fn max_in(xs: &[i32]) -> Option<i32> { // the slice carries its length
    let mut best = *xs.first()?;          // empty slice: None, not a read of xs[0]
    for &x in &xs[1..] {                  // a subslice: a view, nothing copied
        if x > best {
            best = x;
        }
    }
    Some(best)
}

fn main() {
    let xs = [4, 9, 2];
    println!("len = {}", xs.len());
    println!("max = {:?}", max_in(&xs));
    println!("tail max = {:?}", max_in(&xs[2..]));
    println!("empty max = {:?}", max_in(&xs[3..])); // valid and empty
    println!("{:?}", xs.get(3));                    // checked access: None
}
'''

PRACTICE = r'''fn main() {
    let xs = [4, 9, 2];
    let mut best = xs[0];
    for i in 1..=xs.len() {
        if xs[i] > best {
            best = xs[i];
        }
    }
    println!("{best}");
}
'''

LESSON = {
    "title": "Pointer + Length to Slices",
    "concept": "A view that carries its own bounds",
    "minutes": 11,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "A slice `&[T]` is a pointer and a length in one value, so functions receive their bounds and every index is checked.",
        "rule": "A slice borrows a contiguous range of another value's elements; it allocates nothing, and indexing past its length panics instead of reading out of bounds.",
        "explanation": (
            "C arrays decay to pointers at a function boundary, so the length has to travel separately and nothing ties the two together. Inside `max_in`, `sizeof xs` is the size of a pointer, which clang flags with `-Wsizeof-array-argument`, and the `i <= n` off-by-one reads one element past the array: AddressSanitizer reports a `stack-buffer-overflow`.\n\n"
            "A Rust slice `&[i32]` is a fat pointer: the address and the length together. `xs.len()` is always right, and `xs[i]` checks `i < len` and panics with `index out of bounds: the len is 3 but the index is 3` instead of reading the neighbour. When an index may be out of range, `xs.get(i)` returns an `Option`. Arrays, vectors and other slices all coerce to `&[T]`, so one function serves all of them.\n\n"
            "Slicing creates a view, not a copy: `&xs[1..]`, `xs.split_at(mid)` and `xs.windows(2)` borrow the same memory with different bounds. A function that returns a `&[i32]` derived from its `&[i32]` argument is returning a range of the caller's data, and the compiler ties the result's validity to that input, so it cannot outlive the buffer. `&str` is the same idea for UTF-8 text.\n\n"
            "Bounds checks are cheap and are often removed when the compiler can see the index stays in range, which is common in iterator loops. When profiling shows a real cost, iterate instead of indexing, or slice once up front so the later indexes are provably in bounds."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "`max_in` takes a slice, so the length cannot be wrong; an empty slice gives `None`, and `get(3)` is `None` instead of a read past the end.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C function: `longest_run` returns the longest run of equal neighbouring values as a subslice of `xs`, the first one on a tie, and an empty slice for empty input.",
        "success": "`[5, 5, 1, 7, 7, 7]` gives `[7, 7, 7]` even though that run ends the slice, a tie returns the first run, and the result points into the input.",
        "question": "What does the return type of `fn longest_run(xs: &[i32]) -> &[i32]` promise?",
        "answers": [
            "A new heap-allocated copy of the run",
            "A pointer that may outlive `xs`",
            "A fixed-size array of the run's length",
            "A borrowed view into `xs`, valid only while `xs` is",
        ],
        "correctAnswer": 3,
        "feedback": "With one reference input, the result borrows from it: a range of the caller's elements, with no allocation, tied to the input's lifetime.",
        "recall": [
            {
                "question": "What does this print, and does it panic?",
                "code": "let xs = [10, 20, 30];\nlet tail = &xs[3..];\nprintln!(\"{} {:?} {:?}\", tail.len(), xs.get(3), xs.first());",
                "answer": "`0 None Some(10)`, without a panic. A range that starts at the length is valid and gives an empty slice; only an index such as `xs[3]`, or a range that starts past the length, panics.",
            },
            {
                "question": "Why can one function `fn total(xs: &[u32]) -> u32` accept an array, a `Vec` and part of either?",
                "answer": "`&[u32; N]` and `&Vec<u32>` coerce to `&[u32]`, and `&v[a..b]` already is a slice. Every caller passes a pointer and a length the compiler knows, unlike a C `const unsigned *` whose length is passed and trusted separately.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Fuse the arguments", "detail": "Replace each `(const T *p, size_t n)` pair with one `&[T]`, and each writable pair with `&mut [T]`."},
            {"title": "Replace index arithmetic", "detail": "Turn `p + i, n - i` into `&xs[i..]`, and loops that compare neighbours into `windows(2)` or an index loop over `1..xs.len()`."},
            {"title": "Check the ends", "detail": "Test an empty slice, a single element and a run that touches the last element."},
        ],
        "misconception": "“Bounds checking makes slices slow, so real code uses raw pointers.”",
        "correction": "The check is a comparison and a predictable branch, and it disappears when the compiler can prove the index is in range, as it usually can in iterator loops. Measure first; idiomatic Rust rarely needs `get_unchecked`.",
        "transferChallenge": "Write `fn split_header(packet: &[u8]) -> Option<(&[u8], &[u8])>` that returns the first 4 bytes and the rest, or `None` when the packet is shorter than 4 bytes.",
        "connections": [
            {"direction": "previous", "title": "Pointers to References", "concept": "Shared or exclusive, checked at compile time"},
            {"direction": "next", "title": "Dangling Pointers and Lifetimes", "concept": "The compiler checks what the comment promised"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "`sizeof` on an array parameter gives the pointer size, and `i <= n` reads past the end, which AddressSanitizer reports as a stack buffer overflow.",
        "contrasts": [
            {"from": "Pointer and length are separate arguments that can disagree.",
             "rust": "`&[T]` carries both; `len()` is always the real length."},
            {"from": "`xs[n]` reads past the end without a check.",
             "rust": "`xs[n]` panics; `xs.get(n)` returns `None`."},
            {"from": "Arrays decay; `sizeof` inside the callee is the pointer size.",
             "rust": "Arrays and `Vec`s coerce to `&[T]` and keep their length."},
        ],
        "credits": ["ownership/slices"],
    },
}

CHALLENGE = {
    "functions": ["longest_run"],
    "source": r'''// C original:
// /* Returns the length of the longest run of equal neighbours; *start gets its index. */
// size_t longest_run(const int *xs, size_t n, size_t *start) {
//     size_t best = 0, best_start = 0, run = 0;
//     for (size_t i = 0; i < n; i++) {
//         run = (i > 0 && xs[i] == xs[i - 1]) ? run + 1 : 1;
//         if (run > best) { best = run; best_start = i + 1 - run; }
//     }
//     *start = best_start;
//     return best;
// }
pub fn longest_run(xs: &[i32]) -> &[i32] {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;

fn main() {
    assert_eq!(solution::longest_run(&[1, 2, 2, 3]), &[2, 2], "case 1");
    let data = [5, 5, 1, 7, 7, 7];
    let run = solution::longest_run(&data);
    assert_eq!(run, &[7, 7, 7], "case 2: a run that ends the slice");
    assert_eq!(run.as_ptr(), data[3..].as_ptr(), "case 3: a view into the input");
    assert_eq!(solution::longest_run(&[]), &[] as &[i32], "case 4");
    assert_eq!(solution::longest_run(&[4]), &[4], "case 5");
    assert_eq!(solution::longest_run(&[1, 1, 2, 2]), &[1, 1], "case 6: the first run wins a tie");

    println!("PASS c-pointer-length-to-slices");
}
''',
    "cases": [
        ("visible", "solution::longest_run(&[1, 2, 2, 3])", "&[2, 2]"),
        ("boundary", "solution::longest_run(&[5, 5, 1, 7, 7, 7])", "&[7, 7, 7]"),
        ("semantic", "run.as_ptr() == data[3..].as_ptr()", "true"),
        ("boundary", "solution::longest_run(&[])", "&[]"),
        ("boundary", "solution::longest_run(&[4])", "&[4]"),
        ("semantic", "solution::longest_run(&[1, 1, 2, 2])", "&[1, 1]"),
    ],
}

EXPECT = {
    "example": "len = 3\nmax = Some(9)\ntail max = Some(2)\nempty max = None\nNone\n",
    "practice": {"panic": "index out of bounds: the len is 3 but the index is 3"},
    "recall": [{"stdout": "0 None Some(10)\n"}, None],
    "c": {"warnings": ["-Wsizeof-array-argument"], "sanitize": "address", "finding": "stack-buffer-overflow"},
    "wrong": {
        "c-pointer-length-to-slices.1.rs": {"mode": "panic", "note": "closes a run only when the value changes, so a run at the end is lost"},
    },
}
