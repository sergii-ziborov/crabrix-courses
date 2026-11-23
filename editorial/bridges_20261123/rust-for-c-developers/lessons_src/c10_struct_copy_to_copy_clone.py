ID = "c-struct-copy-to-copy-clone"
UNIT = "c-memory"
ORDER = 4

FROM_CODE = r'''#include <stdio.h>
#include <stdlib.h>

struct point { int x, y; };                  /* plain data: copying is fine */
struct path { struct point *pts; size_t len; };

int main(void) {
    struct point p = {1, 2};
    struct point q = p;                       /* an independent copy */
    q.x = 10;
    struct path a = {malloc(2 * sizeof(struct point)), 2};
    a.pts[0] = p;
    a.pts[1] = q;
    struct path b = a;                        /* copies the pointer, not the points */
    b.pts[0].x = 99;                          /* so this also changes a.pts[0] */
    printf("p.x=%d q.x=%d a.pts[0].x=%d\n", p.x, q.x, a.pts[0].x);
    free(a.pts);
    free(b.pts);                              /* ASan: attempting double-free */
    return 0;
}
'''

EXAMPLE = r'''#[derive(Clone, Copy, Debug, PartialEq)]
struct Point {
    x: i32,
    y: i32,
}

#[derive(Clone, Debug)]
struct Path {
    points: Vec<Point>, // owns a heap buffer, so Path cannot be Copy
}

fn main() {
    let p = Point { x: 1, y: 2 };
    let mut q = p;                 // Copy: p is still usable
    q.x = 10;
    let a = Path { points: vec![p, q] };
    let mut b = a.clone();         // an explicit deep copy: a new buffer
    b.points[0].x = 99;
    println!("p.x={} q.x={} q.y={} a.points[0].x={}", p.x, q.x, q.y, a.points[0].x);
    let c = a;                     // a move: still one owner of one buffer
    println!("{} {}", c.points.len(), b.points[0].x);
}
'''

PRACTICE = r'''#[derive(Clone, Copy, Debug, PartialEq)]
struct Point {
    x: i32,
    y: i32,
}

#[derive(Clone, Copy)]
struct Path {
    points: Vec<Point>,
}

fn main() {
    let a = Path { points: vec![Point { x: 1, y: 2 }] };
    let b = a;
    println!("{} {}", a.points.len(), b.points[0].y);
}
'''

LESSON = {
    "title": "Struct Copies: Copy and Clone",
    "concept": "Bitwise copies only for plain data",
    "minutes": 11,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "Rust copies a struct implicitly only when it is plain data marked `Copy`; anything that owns a resource moves, and a deep copy is an explicit `.clone()`.",
        "rule": "`Copy` permits implicit bitwise duplication for types that own no resources; `Clone` is an explicit duplication whose cost depends on the type.",
        "explanation": (
            "C struct assignment always copies bytes. For `struct point` that is exactly right. For `struct path`, which holds a pointer, `b = a` copies the pointer and not the points: the two structs share one buffer, a write through `b` changes `a`, and freeing both is a double free, which AddressSanitizer reports.\n\n"
            "Rust splits this in two. A type can be `Copy` only if all of its fields are `Copy`, which means it owns nothing: integers, `char`, `bool`, shared references, and structs or tuples made of those. Assignment and by-value calls then duplicate the bytes and the source stays usable, exactly like C's `struct point`. `#[derive(Clone, Copy)]` opts a type in.\n\n"
            "A type with a `Vec`, `String` or `Box` field cannot be `Copy`; deriving it is error `E0204`. Assigning such a value moves it: still a bitwise copy of the handle, but the source becomes unusable, so one buffer keeps one owner. When you really want a second, independent buffer, call `.clone()`. The cost is visible at the call site, the opposite of a C struct assignment that may quietly make a shallow copy.\n\n"
            "`Clone` is a trait you derive or implement. For `Vec<Point>` it allocates and copies every element; for `Rc<T>` it only increments a count. Reading `.clone()` tells you that a duplication happens, and the type tells you its price."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "`Point` is `Copy`, so `p` survives `let mut q = p`; `Path` owns a `Vec`, so `b` is an explicit `clone` and `let c = a` is a move.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C functions: `translated` returns a new `Path` with every point moved by `dx` and `dy` and leaves the input unchanged; `first_point` returns a copy of the first point, or `None`.",
        "success": "`translated` returns new points while the original `Path` is unchanged, and `first_point` returns `Some(Point)`, or `None` for an empty path.",
        "question": "Why can `Point { x: i32, y: i32 }` derive `Copy` while `Path { points: Vec<Point> }` cannot?",
        "answers": [
            "`Copy` is limited to structs with at most two fields",
            "`Vec<Point>` is too large to copy",
            "A bitwise copy of a `Vec` would make two owners of one heap buffer, so `Vec` is not `Copy`",
            "`Path` would need `#[repr(C)]` first",
        ],
        "correctAnswer": 2,
        "feedback": "`Copy` requires every field to be `Copy`. `Vec` owns heap memory, so `Path` gets `Clone` for explicit deep copies and moves otherwise.",
        "recall": [
            {
                "question": "Does this compile, and what does it print?",
                "code": "#[derive(Clone, Copy, Debug)]\nstruct Rgb(u8, u8, u8);\n\nfn main() {\n    let a = Rgb(1, 2, 3);\n    let mut b = a;\n    b.0 = 9;\n    println!(\"{a:?} {b:?}\");\n}",
                "answer": "Yes: `Rgb(1, 2, 3) Rgb(9, 2, 3)`. `Rgb` is `Copy`, so `let mut b = a` duplicates the bytes and `a` stays usable and unchanged.",
            },
            {
                "question": "What is the difference in cost between `rc.clone()` on an `Rc<Vec<u8>>` and `v.clone()` on a `Vec<u8>`?",
                "answer": "`rc.clone()` increments a reference count and shares the same vector; `v.clone()` allocates a new buffer and copies every byte. Both are explicit `.clone()` calls; the type tells you which cost you pay.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Classify each field", "detail": "Integers and plain structs are `Copy`; any `Vec`, `String`, `Box` or file handle makes the type move-only."},
            {"title": "Choose per type", "detail": "Derive `Copy` for plain data you would pass by value in C; derive only `Clone` for types that own resources."},
            {"title": "Audit the clones", "detail": "Each `.clone()` is an explicit duplication; confirm it is needed, or borrow instead."},
        ],
        "misconception": "“Moving a value copies all of its data, so moves are expensive.”",
        "correction": "A move copies only the value's own bytes, such as a `Vec`'s pointer, length and capacity, and then forbids using the source. The heap data stays where it is. Only `.clone()` duplicates what the value owns.",
        "transferChallenge": "Add a `name: String` field to `Point` and follow the compiler errors: which derive fails, and where do you now need `.clone()`?",
        "connections": [
            {"direction": "previous", "title": "Dangling Pointers and Lifetimes", "concept": "The compiler checks what the comment promised"},
            {"direction": "next", "title": "Structs and Methods", "concept": "The receiver states the pointer contract"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "Struct assignment copies the pointer, so `b` and `a` share one buffer, and freeing both is a double free.",
        "contrasts": [
            {"from": "Struct assignment always copies bytes, pointers included.",
             "rust": "Only `Copy` types copy implicitly; other types move to a single owner."},
            {"from": "A shallow copy of a struct with a pointer creates two owners.",
             "rust": "A type that owns a `Vec` or `String` cannot be `Copy` (`E0204`)."},
            {"from": "A deep copy is a hand-written function.",
             "rust": "`.clone()` is the explicit deep copy, visible at every call site."},
        ],
        "credits": ["ownership/copy-clone"],
    },
}

CHALLENGE = {
    "functions": ["translated", "first_point"],
    "source": r'''// C original:
// /* Returns a translated deep copy; the caller frees result.pts. The input is unchanged. */
// struct path translated(const struct path *p, int dx, int dy) {
//     struct path out = {malloc(p->len * sizeof *p->pts), p->len};
//     for (size_t i = 0; i < p->len; i++)
//         out.pts[i] = (struct point){p->pts[i].x + dx, p->pts[i].y + dy};
//     return out;
// }
// /* Copies the first point into *out; returns 0 when the path is empty. */
// int first_point(const struct path *p, struct point *out);
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Point {
    pub x: i32,
    pub y: i32,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Path {
    pub points: Vec<Point>,
}

pub fn translated(path: &Path, dx: i32, dy: i32) -> Path {
    todo!("implement the contract")
}

pub fn first_point(path: &Path) -> Option<Point> {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;
use solution::{Path, Point};

fn main() {
    let original = Path { points: vec![Point { x: 1, y: 2 }, Point { x: -3, y: 0 }] };
    let moved = solution::translated(&original, 10, -1);
    assert_eq!(moved.points, vec![Point { x: 11, y: 1 }, Point { x: 7, y: -1 }], "case 1");
    assert_eq!(original.points, vec![Point { x: 1, y: 2 }, Point { x: -3, y: 0 }], "case 2: the input is unchanged");
    let empty = Path { points: Vec::new() };
    assert_eq!(solution::translated(&empty, 5, 5), empty, "case 3");
    assert_eq!(solution::first_point(&original), Some(Point { x: 1, y: 2 }), "case 4");
    assert_eq!(solution::first_point(&empty), None, "case 5");

    println!("PASS c-struct-copy-to-copy-clone");
}
''',
    "cases": [
        ("visible", "solution::translated(&[(1, 2), (-3, 0)], 10, -1)", "[(11, 1), (7, -1)]"),
        ("semantic", "original after translated", "unchanged"),
        ("boundary", "solution::translated(&empty, 5, 5)", "empty"),
        ("visible", "solution::first_point(&original)", "Some(Point { x: 1, y: 2 })"),
        ("boundary", "solution::first_point(&empty)", "None"),
    ],
}

EXPECT = {
    "example": "p.x=1 q.x=10 q.y=2 a.points[0].x=1\n2 99\n",
    "practice": {"errors": ["E0204"]},
    "recall": [{"stdout": "Rgb(1, 2, 3) Rgb(9, 2, 3)\n"}, None],
    "c": {"warnings": [], "exit": -5, "sanitize": "address", "finding": "attempting double-free"},
    "wrong": {
        "c-struct-copy-to-copy-clone.1.rs": {"mode": "compile error E0507", "note": "C habit: a shallow struct copy, moving the borrowed `Vec` out of `path`"},
    },
}
