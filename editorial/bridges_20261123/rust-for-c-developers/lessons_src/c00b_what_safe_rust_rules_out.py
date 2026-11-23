ID = "c-what-safe-rust-rules-out"
UNIT = "c-rust-at-a-glance"
ORDER = 1

FROM_CODE = r'''#include <stdio.h>
#include <stdlib.h>

/* Every case compiles cleanly with -Wall -Wextra.
   Every case except 0 is undefined behaviour when it runs. */
int main(int argc, char **argv) {
    int which = argc > 1 ? atoi(argv[1]) : 0;
    int xs[3] = {1, 2, 3};
    int *null = NULL;
    int *heap = malloc(sizeof *heap);
    if (!heap) return 1;
    *heap = 7;
    if (which == 1) printf("%d\n", xs[which + 2]);           /* out of bounds */
    if (which == 2) { free(heap); printf("%d\n", *heap); }   /* use after free */
    if (which == 3) printf("%d\n", *null);                   /* null dereference */
    if (which == 4) free(heap);                              /* the first free... */
    if (which != 2) free(heap);                              /* ...and a double free */
    printf("case %d done\n", which);
    return 0;
}
'''

EXAMPLE = r'''fn main() {
    let xs = [1, 2, 3];
    let i = std::env::args().count() + 2;       // 3 when run without arguments
    println!("{:?}", xs.get(i));                // checked access: None
    let heap = Box::new(7);
    let owner = heap;                           // moved: `heap` is no longer usable
    println!("{owner}");
    let missing: Option<&i32> = None;           // no null references, only Option
    println!("{}", missing.copied().unwrap_or(0));
    let sum = 200u8.wrapping_add(100);          // wrapping you asked for: 44
    println!("{sum}");
    let leaked: &'static mut i32 = Box::leak(Box::new(1)); // a leak is safe
    *leaked += 1;
    println!("{leaked}");
}
'''

PRACTICE = r'''fn main() {
    let total: i32;
    let ready = std::env::args().count() > 1;
    if ready {
        total = 10;
    }
    println!("{total}");
}
'''

LESSON = {
    "title": "What Safe Rust Rules Out",
    "concept": "Undefined behaviour excluded, bugs still possible",
    "minutes": 12,
    "exerciseKind": "planned",
    "writing": {
        "summary": "Safe Rust rules out the memory and thread bugs that are undefined behaviour in C, but not leaks, deadlocks, panics or wrong logic.",
        "rule": "Safe Rust has no undefined behaviour: use after free, double free, dangling references, out-of-bounds access, null dereference, uninitialised reads and data races are rejected or checked; leaks, deadlocks, panics, logic errors and wrapping arithmetic in release builds are not.",
        "explanation": (
            "In C, executing an undefined operation makes the whole program meaningless, and the optimiser is allowed to assume it never happens. The example's four cases compile without a single warning under `-Wall -Wextra`; each one fails only when it runs, and only a sanitizer build says why: `stack-buffer-overflow`, `heap-use-after-free`, a load of a null pointer and `attempting double-free`.\n\n"
            "Safe Rust closes each of these by construction. Ownership means one owner frees each value once, so double free and use after free cannot be written. Borrow checking means a reference cannot outlive its value or overlap a writer. References are never null; absence is `Option`. A binding must be initialised on every path before it is read, or the program is rejected with `E0381`. `Send` and `Sync`, together with borrowing, make data races a compile error. Indexing is the one run-time check: `xs[i]` with a bad index panics, and `xs.get(i)` returns `None`, so an out-of-bounds read never touches the neighbouring memory.\n\n"
            "\"Safe\" means free of undefined behaviour, not correct. Safe Rust can still leak memory (`Box::leak`, `mem::forget` and `Rc` cycles are all safe), deadlock on two `Mutex`es taken in different orders, compute the wrong answer, run out of memory or stack, and panic. A panic is defined behaviour: the thread unwinds and runs destructors, or the process aborts if it is configured to. Integer overflow is defined too, but in release builds it wraps unless you choose `checked_` or keep `overflow-checks` on.\n\n"
            "`unsafe` re-enables specific powers that safe code lacks: dereferencing raw pointers, calling `unsafe` functions including every C function, accessing mutable statics, implementing `unsafe` traits and reading `union` fields. Inside those blocks every C undefined behaviour is possible again, and the guarantee for the whole program rests on each `unsafe` block being right. That is why such blocks are kept small and documented; a later lesson shows how."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "A checked index, a move instead of a second owner, `Option` instead of null, explicit wrapping, and a leak that is wasteful but safe.",
        "practiceCode": PRACTICE,
        "task": "Run the C program's cases under a sanitizer in your head, match each one to the Rust rule that excludes it, then decide what the practice program needs before it compiles.",
        "success": "You can name the Rust mechanism behind each excluded C bug, and list three kinds of bug safe Rust still allows.",
        "question": "Which of these can a program written entirely in safe Rust still do?",
        "answers": [
            "Read a freed heap buffer through a stale reference",
            "Index one element past the end of an array without being stopped",
            "Dereference a null reference",
            "Leak memory with `Box::leak` or deadlock on two `Mutex`es",
        ],
        "correctAnswer": 3,
        "feedback": "Leaks and deadlocks are bugs, not undefined behaviour, so safe Rust allows them. The other three are rejected at compile time or stopped by a bounds-check panic.",
        "recall": [
            {
                "question": "Is a panic in Rust undefined behaviour, like an out-of-bounds read in C?",
                "answer": "No. A panic is defined: by default the thread unwinds, runs destructors and reports the message, and with `panic = \"abort\"` the process stops immediately. A bad index in safe Rust becomes this defined panic instead of a read of neighbouring memory.",
            },
            {
                "question": "Does this compile, and is it safe?",
                "code": "fn main() {\n    let data = vec![0u8; 1024];\n    std::mem::forget(data);\n    println!(\"done\");\n}",
                "answer": "Yes and yes: it prints `done`. Leaking is not undefined behaviour, so `mem::forget`, `Box::leak` and `Rc` cycles are all safe. The memory is never returned to the allocator, which wastes it but cannot corrupt anything.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "List the undefined cases", "detail": "For a C function, write down every place it relies on a pointer being valid, an index being in range or a variable being set."},
            {"title": "Match the mechanism", "detail": "Ownership, borrowing, `Option`, initialisation checks, bounds checks and `Send`/`Sync` each exclude one of them in safe Rust."},
            {"title": "Keep the remaining risks", "detail": "Leaks, deadlocks, panics, overflow policy and logic still need tests and review, as in C."},
        ],
        "misconception": "“If it compiles in Rust, it is correct.”",
        "correction": "If it compiles without `unsafe`, it has no undefined behaviour. It can still leak, deadlock, panic or compute the wrong result; the compiler removes a class of bugs, not the need for tests.",
        "transferChallenge": "Write a safe Rust program that deadlocks with two `Mutex`es locked in opposite orders by two threads, then fix it with one global lock order.",
        "connections": [
            {"direction": "previous", "title": "What Rust Is, from C", "concept": "Native code and the same machine, with checks before it runs"},
            {"direction": "next", "title": "Reading rustc Diagnostics", "concept": "Compile-time errors instead of run-time crashes"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "Four undefined behaviours that compile without a warning; sanitizers report a stack overflow, a use after free, a null load and a double free.",
        "contrasts": [
            {"from": "Use after free, double free and dangling pointers compile and are undefined.",
             "rust": "Ownership and borrow checking reject them at compile time."},
            {"from": "Out-of-bounds reads and NULL dereferences are undefined.",
             "rust": "Indexing is bounds-checked (a defined panic); absence is `Option`, never a null reference."},
            {"from": "Reading an uninitialised variable is at most a warning.",
             "rust": "Every binding must be initialised on every path before it is read (`E0381`)."},
            {"from": "Leaks, deadlocks and logic errors are the programmer's problem.",
             "rust": "They still are: safe Rust excludes undefined behaviour, not bugs."},
        ],
        "credits": [],
    },
}

EXPECT = {
    "example": "None\n7\n0\n44\n2\n",
    "practice": {"errors": ["E0381"]},
    "recall": [None, {"stdout": "done\n"}],
    "probes": {
        "index-panics": {"code": "let xs = [1, 2, 3];\nlet i = std::env::args().count() + 2;\nprintln!(\"{}\", xs[i]);", "panic": "index out of bounds: the len is 3 but the index is 3"},
        "double-owner-rejected": {"code": "let heap = Box::new(7);\nlet owner = heap;\nprintln!(\"{heap} {owner}\");", "errors": ["E0382"]},
        "data-race-rejected": {"code": "let mut hits = 0;\nlet a = std::thread::spawn(|| hits += 1);\nhits += 1;\na.join().unwrap();", "errors": ["E0373", "E0503"]},
        "static-mut-needs-unsafe": {"code": "static mut COUNTER: u32 = 0;\nfn main() {\n    COUNTER += 1;\n}", "errors": ["E0133"]},
    },
    "c": {"warnings": [], "stdout": "case 0 done\n", "exit": 0,
          "sanitizeRuns": [
              {"args": ["1"], "sanitize": "address,undefined", "finding": "stack-buffer-overflow"},
              {"args": ["2"], "sanitize": "address,undefined", "finding": "heap-use-after-free"},
              {"args": ["3"], "sanitize": "address,undefined", "finding": "load of null pointer"},
              {"args": ["4"], "sanitize": "address,undefined", "finding": "attempting double-free"},
          ]},
}
