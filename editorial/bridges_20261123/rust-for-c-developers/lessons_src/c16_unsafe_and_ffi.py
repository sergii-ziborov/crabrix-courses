ID = "c-unsafe-and-ffi"
UNIT = "c-systems"
ORDER = 1

FROM_CODE = r'''#include <stdint.h>
#include <stdio.h>

struct pair {          /* C layout: tag, 3 padding bytes, value */
    uint8_t tag;
    uint32_t value;
};

/* The caller promises xs points to n readable int32_t values. */
int32_t sum_i32(const int32_t *xs, size_t n) {
    int32_t total = 0;
    for (size_t i = 0; i < n; i++) total += xs[i];
    return total;
}

int main(void) {
    int32_t xs[] = {1, 2, 3};
    struct pair p = {7, 42};
    printf("%d size=%zu tag=%u value=%u\n", sum_i32(xs, 3), sizeof p, p.tag, p.value);
    return 0;
}
'''

EXAMPLE = r'''use std::slice;

#[repr(C)] // C field order and padding: tag, 3 padding bytes, value
struct Pair {
    tag: u8,
    value: u32,
}

/// # Safety
/// `xs` must be non-null, aligned and point to `n` initialised `i32`s
/// that nothing mutates during the call.
unsafe extern "C" fn sum_i32(xs: *const i32, n: usize) -> i32 {
    // SAFETY: the caller upholds the contract documented above.
    let values = unsafe { slice::from_raw_parts(xs, n) };
    values.iter().sum() // from here on: ordinary, bounds-checked Rust
}

unsafe extern "C" {
    fn abs(x: i32) -> i32; // from the C library; the declaration is a promise
}

fn main() {
    let xs = [1, 2, 3];
    let p = Pair { tag: 7, value: 42 };
    // SAFETY: `xs` is a live array of 3 `i32`s, and `abs` has this C signature.
    let (total, magnitude) = unsafe { (sum_i32(xs.as_ptr(), xs.len()), abs(-5)) };
    println!("{total} size={} tag={} value={} abs={magnitude}", size_of::<Pair>(), p.tag, p.value);
}
'''

PRACTICE = r'''fn main() {
    let x = 5;
    let p = &x as *const i32; // creating a raw pointer is safe
    let y = *p;               // dereferencing it is not
    println!("{y}");
}
'''

LESSON = {
    "title": "unsafe, Raw Pointers and FFI",
    "concept": "Where Rust hands the proof back to you",
    "minutes": 14,
    "exerciseKind": "planned",
    "writing": {
        "summary": "Raw pointers, `unsafe` and `extern \"C\"` let Rust do what C does, and `unsafe` marks exactly where you take over the proof that the compiler cannot do.",
        "rule": "Creating a raw pointer is safe; dereferencing it needs `unsafe`, which is a claim that the pointer is valid, aligned, initialised and correctly aliased, not a switch that turns the checks off.",
        "explanation": (
            "Everything in C is the programmer's proof: the pointer is valid, `n` is the real length, nothing else writes meanwhile. Rust keeps that model available. `*const T` and `*mut T` are raw pointers with no lifetime and no aliasing guarantees, and creating one with `as` or `as_ptr()` is safe, because nothing can go wrong until it is used.\n\n"
            "Dereferencing a raw pointer, calling an `unsafe fn` (every foreign function is one), accessing a mutable `static` and reading a `union` field need an `unsafe` block; implementing an `unsafe trait` needs `unsafe impl`. Inside the block the compiler still applies every other rule, including type checks, borrow checks and slice bounds checks. What `unsafe` adds is your claim that the invariants it cannot check hold. Write that claim down: a `# Safety` section on an `unsafe fn` lists the caller's obligations, and a `// SAFETY:` comment on a block says why they are met.\n\n"
            "The common pattern is a thin unsafe edge around safe code. `slice::from_raw_parts(ptr, len)` turns a C pointer and length into a `&[i32]`, and from then on indexing is checked again. The obligations of that one call are exactly what the C contract said in prose: non-null, aligned, `len` initialised elements, and no mutation while the slice is in use.\n\n"
            "For FFI, `#[repr(C)]` gives a struct C's field order and padding for the target, so `Pair` is 8 bytes like `struct pair`; without it, Rust may reorder fields. It does not make the field types themselves C-compatible or make pointers valid. In edition 2024, foreign declarations go in an `unsafe extern \"C\" { ... }` block, and a Rust function exported to C is an `extern \"C\" fn` marked `#[unsafe(no_mangle)]`. Calling C needs `unsafe` because the compiler cannot check the declaration against the C side."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "`#[repr(C)]` keeps C's layout, `sum_i32` turns a pointer and a length into a slice inside one documented `unsafe` block, and `abs` comes from the C library.",
        "practiceCode": PRACTICE,
        "task": "Decide which line of the quiz needs `unsafe` and what that block asserts, then fix the practice program without changing what it prints.",
        "success": "You can name the one operation that needs `unsafe` and the facts the block asserts about the pointer: non-null, aligned, pointing to a live, initialised value.",
        "question": "In `let p = &x as *const i32; let q = p.wrapping_add(1); let v = *p; println!(\"{p:?} {q:?}\");`, which operation needs `unsafe`, and what does the block claim?",
        "answers": [
            "`*p`: the block claims `p` is non-null, aligned and points to a live, initialised `i32`",
            "Creating `p`: a raw pointer turns off the borrow checker",
            "`p.wrapping_add(1)` and `*p`: all raw pointer arithmetic is unsafe",
            "Every line: inside `unsafe` the compiler skips its checks",
        ],
        "correctAnswer": 0,
        "feedback": "Creating a raw pointer, offsetting it with `wrapping_add` and printing it are safe. Only the dereference relies on facts the compiler cannot check.",
        "recall": [
            {
                "question": "What must be true for `unsafe { std::slice::from_raw_parts(ptr, len) }` to be sound when `ptr` comes from C?",
                "answer": "`ptr` is non-null and aligned, points to `len` consecutive initialised values of the element type within one allocation, the total size is at most `isize::MAX` bytes, and nothing mutates that memory while the slice is in use. These are the obligations in the function's `# Safety` documentation.",
            },
            {
                "question": "Why is this `Header` not safe to pass to a C function that expects `struct header { uint16_t len; uint8_t kind; }`?",
                "code": "struct Header {\n    len: u16,\n    kind: u8,\n}",
                "answer": "Without `#[repr(C)]`, Rust guarantees neither field order nor padding, so the layout may differ from the C struct. Add `#[repr(C)]` and compare `size_of::<Header>()` with `sizeof(struct header)`.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Find the obligations", "detail": "For each `unsafe` operation, write down the conditions it needs, taken from its `# Safety` documentation."},
            {"title": "Shrink the block", "detail": "Keep only the operation that needs `unsafe` inside the block, and convert to a safe type such as a slice as early as possible."},
            {"title": "Document the proof", "detail": "Add a `// SAFETY:` comment that says why each condition holds at this call."},
        ],
        "misconception": "“Inside `unsafe`, Rust behaves like C and checks nothing.”",
        "correction": "Types, borrows and slice bounds are still checked inside `unsafe`. The block only permits a few extra operations, such as dereferencing a raw pointer or calling an `unsafe fn`, and makes you responsible for their preconditions.",
        "transferChallenge": "Export `sum_i32` to C as `#[unsafe(no_mangle)] pub unsafe extern \"C\" fn`, write the matching C prototype, and list which `# Safety` conditions the C caller must now uphold.",
        "connections": [
            {"direction": "previous", "title": "Headers and make to Cargo", "concept": "Modules, pub and the crate as the build unit"},
            {"direction": "next", "title": "pthreads to std::thread", "concept": "Locks that own data, threads that own their captures"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "The pointer-and-length contract and the struct layout are stated only in comments.",
        "contrasts": [
            {"from": "Every pointer dereference is trusted.",
             "rust": "Only operations inside `unsafe` are trusted; everything else stays checked."},
            {"from": "The contract of `(ptr, n)` is prose.",
             "rust": "`# Safety` docs and `// SAFETY:` comments mark the proof at each `unsafe`."},
            {"from": "Struct layout follows the C ABI.",
             "rust": "Rust may reorder fields; `#[repr(C)]` requests C layout."},
        ],
        "credits": ["systems/unsafe", "systems/raw-pointers"],
    },
}

EXPECT = {
    "example": "6 size=8 tag=7 value=42 abs=5\n",
    "practice": {"errors": ["E0133"]},
    "recall": [None, {"compiles": True}],
    "probes": {
        "quiz-safe-lines": {"code": "let x = 5;\nlet p = &x as *const i32;\nlet q = p.wrapping_add(1);\nprintln!(\"{}\", p != q);", "stdout": "true\n"},
        "quiz-deref": {"code": "let x = 5;\nlet p = &x as *const i32;\nlet v = *p;\nprintln!(\"{v}\");", "errors": ["E0133"]},
        "repr-c-header-size": {"code": "#[repr(C)]\nstruct Header { len: u16, kind: u8 }\nfn main() {\n    let h = Header { len: 1, kind: 2 };\n    println!(\"{} {} {}\", size_of::<Header>(), h.len, h.kind);\n}", "stdout": "4 1 2\n"},
    },
    "c": {"warnings": [], "stdout": "6 size=8 tag=7 value=42\n", "exit": 0},
}
