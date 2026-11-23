ID = "c-pointers-to-references"
UNIT = "c-memory"
ORDER = 1

FROM_CODE = r'''#include <stdio.h>
#include <stdlib.h>

struct ivec { int *data; size_t len, cap; };

static void push(struct ivec *v, int x) {
    if (v->len == v->cap) {
        v->cap = v->cap ? v->cap * 2 : 1;
        v->data = realloc(v->data, v->cap * sizeof *v->data); /* may move */
    }
    v->data[v->len++] = x;
}

int main(void) {
    struct ivec v = {0};
    push(&v, 1);
    int *first = &v.data[0];  /* a pointer into the buffer */
    push(&v, 2);              /* realloc may have moved the buffer */
    printf("%d\n", *first);   /* ASan: heap-use-after-free */
    free(v.data);
    return 0;
}
'''

EXAMPLE = r'''fn sum(values: &[i32]) -> i32 { // a shared borrow: read-only access
    values.iter().sum()
}

fn main() {
    let mut v = vec![1];
    let first = v[0];   // copy the i32 out instead of keeping a borrow
    v.push(2);          // needs `&mut v`: no other borrow may be in use
    println!("{first}");
    let total = sum(&v); // lend `v` for reading; main still owns it
    v.push(3);
    println!("{total} {v:?}");
}
'''

PRACTICE = r'''fn main() {
    let mut v = vec![1];
    let first = &v[0];
    v.push(2);
    println!("{first}");
}
'''

LESSON = {
    "title": "Pointers to References",
    "concept": "Shared or exclusive, checked at compile time",
    "minutes": 13,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "A reference is a pointer the compiler checks: shared `&T` for reading, or one exclusive `&mut T` for writing, never both at once.",
        "rule": "At any point a value has either any number of shared borrows `&T` or exactly one mutable borrow `&mut T`, never both; a borrow lends access without transferring ownership.",
        "explanation": (
            "The C program keeps `int *first` into a dynamic array and then pushes. `realloc` may move the buffer, so `first` can dangle: AddressSanitizer reports `heap-use-after-free`, while a plain build may print the right number by luck. The bug is not the pointer itself but the combination of a reader that keeps a pointer and a writer that changes the buffer it points into.\n\n"
            "Rust references are pointers with two rules that the compiler enforces. `&T` is shared: any number may exist, and none of them can mutate the value. It is like `const T *`, plus the guarantee that nobody else mutates the value while the borrow is in use. `&mut T` is exclusive: while it is in use, no other reference to the value may be used, which is what C's `restrict` promises and never checks. `v.push(2)` needs `&mut v`, so with `first = &v[0]` still in use, rustc reports `E0502`.\n\n"
            "A borrow lasts until its last use, not until the end of the scope. Moving the `println!` above the push, or copying the `i32` out with `let first = v[0];`, removes the conflict. References are never null and always point at a live value, so the defensive `if (!p) return -1;` at the top of a C function disappears for references; `Option<&T>` is the type when absence is possible.\n\n"
            "Borrowing is also how a function reads data without taking ownership: `fn sum(values: &[i32])` reads the caller's vector and leaves it with the caller. The aliasing bug in the challenge's C original, `append_doubled(v, v->data, v->len)`, cannot be written in Rust: a `&mut dst` and a `&dst` in the same call are rejected."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "The value is copied out before `push`, and `sum` borrows `v` for reading only, so the later `push` is allowed.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C function: `append_doubled` pushes twice each value of `src` onto the end of `dst` and leaves `src` with the caller.",
        "success": "Values are appended after the existing ones, an empty `src` changes nothing, and `src` is still usable after the call.",
        "question": "Why does rustc reject `let first = &v[0]; v.push(2); println!(\"{first}\");`?",
        "answers": [
            "`v[0]` cannot be borrowed because `i32` is `Copy`",
            "`first` is a shared borrow still in use when `push` needs a mutable borrow of `v`",
            "`push` takes `v` by value, so `v` has moved",
            "Elements of a vector cannot be borrowed; you must use an index",
        ],
        "correctAnswer": 1,
        "feedback": "The shared borrow lives until the `println!`. Print before pushing, or copy the value out with `let first = v[0];`, and the mutable borrow no longer overlaps it.",
        "recall": [
            {
                "question": "Does this compile?",
                "code": "let mut v = vec![1, 2];\nlet first = &v[0];\nprintln!(\"{first}\");\nv.push(3);\nprintln!(\"{v:?}\");",
                "answer": "Yes, and it prints `1` and `[1, 2, 3]`. The shared borrow `first` is last used in the first `println!`, so it has ended before `push` takes `&mut v`. Borrows last until their last use, not until the end of the scope.",
            },
            {
                "question": "What contract does `fn fill(dst: &mut [u8], src: &[u8])` state that the C prototype `void fill(uint8_t *dst, const uint8_t *src, size_t n)` does not?",
                "answer": "That `dst` and `src` do not overlap and that each is valid for its own length. A caller cannot pass the same buffer as both, because a `&mut` and a `&` to it cannot coexist. In C that takes `restrict` plus documentation, and nothing checks it.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "List the borrows", "detail": "Mark every `&` and `&mut`, including implicit ones such as the `&mut v` that `v.push` takes."},
            {"title": "Find each last use", "detail": "A borrow ends at its last use; draw a line from where it is created to that point."},
            {"title": "Look for overlap", "detail": "A `&mut` that crosses a live `&` is `E0502`; reorder the code or copy the value out."},
        ],
        "misconception": "“A shared reference is just `const T *`.”",
        "correction": "`const T *` only stops you writing through that pointer; other code may still change the value. `&T` also guarantees that nothing mutates the value while the borrow is in use (outside interior-mutability types such as `Cell`), which is why the compiler can reject the `push`.",
        "transferChallenge": "Call `append_doubled(&mut v, &v)` in your own `main` and read which two borrows rustc names; then make it compile with an explicit copy, `let snapshot = v.clone();`.",
        "connections": [
            {"direction": "previous", "title": "From malloc/free to Ownership", "concept": "One owner frees, exactly once"},
            {"direction": "next", "title": "Pointer + Length to Slices", "concept": "A view that carries its own bounds"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "`first` points into the old buffer after `realloc`; AddressSanitizer reports a heap use after free.",
        "contrasts": [
            {"from": "Any number of `T *` may read and write at the same time.",
             "rust": "Many `&T` readers or one `&mut T` writer at a time; a conflict is `E0502`."},
            {"from": "`restrict` promises no aliasing, unchecked.",
             "rust": "`&mut T` is exclusive, and the compiler checks it."},
            {"from": "A pointer may be NULL or dangle; callers check by hand.",
             "rust": "A reference is never null and cannot outlive its value."},
        ],
        "credits": ["basics/references-intro", "ownership/borrowing"],
    },
}

CHALLENGE = {
    "functions": ["append_doubled"],
    "source": r'''// C original:
// /* Appends 2 * src[i] to dst. With src == dst->data this reads freed memory
//    as soon as push() reallocates. */
// void append_doubled(struct ivec *dst, const int *src, size_t n) {
//     for (size_t i = 0; i < n; i++) push(dst, 2 * src[i]);
// }
pub fn append_doubled(dst: &mut Vec<i32>, src: &[i32]) {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;

fn main() {
    let mut dst = vec![10];
    let src = vec![1, 2, 3];
    solution::append_doubled(&mut dst, &src);
    assert_eq!(dst, vec![10, 2, 4, 6], "case 1");
    assert_eq!(src, vec![1, 2, 3], "case 2: the caller still owns src");
    solution::append_doubled(&mut dst, &[]);
    assert_eq!(dst, vec![10, 2, 4, 6], "case 3");
    let snapshot = dst.clone();
    solution::append_doubled(&mut dst, &snapshot);
    assert_eq!(dst, vec![10, 2, 4, 6, 20, 4, 8, 12], "case 4");
    let mut empty = Vec::new();
    solution::append_doubled(&mut empty, &[-5, 0]);
    assert_eq!(empty, vec![-10, 0], "case 5");

    println!("PASS c-pointers-to-references");
}
''',
    "cases": [
        ("visible", "append_doubled(&mut vec![10], &[1, 2, 3])", "dst == [10, 2, 4, 6]"),
        ("semantic", "src after the call", "[1, 2, 3]"),
        ("boundary", "append_doubled(&mut dst, &[])", "dst unchanged"),
        ("semantic", "append_doubled(&mut dst, &dst.clone())", "[10, 2, 4, 6, 20, 4, 8, 12]"),
        ("boundary", "append_doubled(&mut Vec::new(), &[-5, 0])", "[-10, 0]"),
    ],
}

EXPECT = {
    "example": "1\n3 [1, 2, 3]\n",
    "practice": {"errors": ["E0502"]},
    "recall": [{"stdout": "1\n[1, 2, 3]\n"}, None],
    "probes": {
        "aliasing-call": {"code": "fn append_doubled(dst: &mut Vec<i32>, src: &[i32]) {\n    for &x in src { dst.push(x * 2); }\n}\nfn main() {\n    let mut v = vec![1];\n    append_doubled(&mut v, &v);\n}", "errors": ["E0502"]},
    },
    "c": {"warnings": [], "exit": 0, "sanitize": "address", "finding": "heap-use-after-free"},
    "wrong": {
        "c-pointers-to-references.1.rs": {"mode": "panic", "note": "C habit: reserve capacity, then write past `len()` by index"},
    },
}
