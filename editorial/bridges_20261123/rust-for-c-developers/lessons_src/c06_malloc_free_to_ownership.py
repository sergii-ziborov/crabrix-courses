ID = "c-malloc-free-to-ownership"
UNIT = "c-memory"
ORDER = 0

FROM_CODE = r'''#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Takes ownership and frees the report. Only this comment says so. */
static void archive(char *report) {
    printf("archived %s\n", report);
    free(report);
}

int main(void) {
    char *report = strdup("q3-summary");
    archive(report);
    free(report);                 /* ASan: attempting double-free */
    return 0;
}
'''

EXAMPLE = r'''struct Noisy(&'static str);

impl Drop for Noisy {
    fn drop(&mut self) {
        println!("drop {}", self.0); // runs once, when the owner goes away
    }
}

fn archive(report: String) { // takes ownership; the String is freed here
    println!("archived {report}");
}

fn main() {
    let report = String::from("q3-summary");
    archive(report);             // moved: `report` can no longer be used
    let _log = Noisy("log");
    let _lock = Noisy("lock");
    let _file = Noisy("file");
    println!("end of main");
}                                // drops in reverse: file, lock, log
'''

PRACTICE = r'''fn archive(report: String) {
    println!("archived {report}");
}

fn main() {
    let report = String::from("q3-summary");
    archive(report);
    println!("{report}");
}
'''

LESSON = {
    "title": "From malloc/free to Ownership",
    "concept": "One owner frees, exactly once",
    "minutes": 13,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "Every heap value in Rust has exactly one owner; passing it by value moves ownership, and the end of the owner's scope frees it exactly once.",
        "rule": "One value has one owner; a move transfers ownership and ends the old binding, and the remaining owners drop in reverse declaration order at the end of their scope.",
        "explanation": (
            "In C, ownership of a `malloc` result is a convention written in comments: who frees it, and when. Getting it wrong has three outcomes: a leak, a use after free or a double free. The example's `archive()` frees its argument and the caller frees it again. Nothing in `void archive(char *)` says the pointer is consumed, so the compiler cannot help; AddressSanitizer reports `attempting double-free`, and a plain macOS build is killed by a trap inside `free`.\n\n"
            "Rust makes the convention part of the type. `String`, `Vec<T>` and `Box<T>` own their heap memory. A parameter of type `String` takes ownership: after `archive(report)` the value has moved, and any later use of `report` is error `E0382`, borrow of moved value. The value is freed once, by its final owner, when that owner goes out of scope. There is no `free` to call and none to forget on an early return.\n\n"
            "A move copies only the handle (pointer, length and capacity) and then treats the source as uninitialised; nothing is deep-copied unless you call `.clone()`. Returning a value moves it out to the caller, which is how a Rust function hands back ownership, like a C function returning a pointer the caller must free.\n\n"
            "Cleanup order is defined. At the end of a scope, the remaining locals drop in reverse declaration order, the order a careful `goto cleanup` chain releases resources. The `Drop` trait runs code at that point, so the same mechanism closes files and releases locks. `drop(x)` ends a value early by moving it into a function that does nothing with it."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "`archive` consumes `report`; the three `Noisy` values drop in reverse order (`file`, `lock`, `log`) after `end of main`.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C function: `take_largest` returns the longest buffer (the first one on a tie) without copying it, drops all the others, and returns `None` for an empty list.",
        "success": "The returned `Vec` has the same heap pointer as the buffer it came from, a tie returns the first longest buffer, and an empty list gives `None`.",
        "question": "A function declares `let _log = Noisy(\"log\"); let _lock = Noisy(\"lock\"); let _file = Noisy(\"file\");`. In which order do their `Drop` implementations run at its closing brace?",
        "answers": [
            "`log`, `lock`, `file`: declaration order",
            "In an unspecified order, as with a garbage collector",
            "`file`, `lock`, `log`: reverse declaration order",
            "None of them run there: names starting with `_` are dropped immediately",
        ],
        "correctAnswer": 2,
        "feedback": "Remaining locals drop in reverse declaration order. A leading underscore only silences the unused-variable warning; `_log` still owns its value until the scope ends.",
        "recall": [
            {
                "question": "How does a Rust function return ownership of a heap buffer, the way a C function returns a pointer the caller must free?",
                "answer": "It returns the owning type by value, such as `Vec<u8>` or `String`. The return moves the handle to the caller, who becomes the owner and frees it by letting it go out of scope. The heap data is not copied.",
            },
            {
                "question": "Does this compile? If not, what is the smallest fix?",
                "code": "fn consume(v: Vec<u8>) -> usize {\n    v.len()\n}\n\nfn main() {\n    let data = vec![1, 2, 3];\n    let n = consume(data);\n    println!(\"{n} {}\", data.len());\n}",
                "answer": "No: `data` moved into `consume`, so `data.len()` is error `E0382`. Read the length before the call, or change `consume` to borrow (`v: &[u8]`) and call `consume(&data)`.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Find each owner", "detail": "For each `String`, `Vec` or `Box`, name the binding that owns it on each line."},
            {"title": "Mark the moves", "detail": "Every by-value argument, assignment or return moves ownership; after it, the old name is unusable."},
            {"title": "Place the drops", "detail": "At each closing brace, list the remaining owners in reverse declaration order."},
        ],
        "misconception": "“Rust frees memory with a garbage collector, so cleanup happens at some later time.”",
        "correction": "There is no collector. The compiler inserts the drop at a known point: the end of the final owner's scope, or the call to `drop`. That point is visible in the source, exactly where a careful C programmer would have called `free`.",
        "transferChallenge": "Change `archive` to take `&str` so the caller keeps `report`, then return a `String` from a helper function and trace which binding finally frees it.",
        "connections": [
            {"direction": "previous", "title": "From for(;;) to Ranges", "concept": "Ranges, iterators and loop with a value"},
            {"direction": "next", "title": "Pointers to References", "concept": "Shared or exclusive, checked at compile time"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "`archive()` frees its argument, so the caller's `free` is a double free that AddressSanitizer reports.",
        "contrasts": [
            {"from": "Who calls `free` is a comment-level convention.",
             "rust": "The owner frees; ownership is in the type: `String`, `Vec<T>`, `Box<T>`."},
            {"from": "Using a pointer after the callee freed it compiles.",
             "rust": "Using a moved value is error `E0382`."},
            {"from": "Cleanup on every exit path, often `goto cleanup` in reverse order.",
             "rust": "Locals drop in reverse declaration order on every exit path."},
        ],
        "credits": ["ownership/ownership", "ownership/drop-order"],
    },
}

CHALLENGE = {
    "functions": ["take_largest"],
    "source": r'''// C original:
// /* Returns the longest buffer (the first on a tie) and frees all the others.
//    The caller owns the result and must free it. */
// unsigned char *take_largest(unsigned char **bufs, size_t *lens, size_t n, size_t *out_len) {
//     if (n == 0) return NULL;
//     size_t best = 0;
//     for (size_t i = 1; i < n; i++) if (lens[i] > lens[best]) best = i;
//     for (size_t i = 0; i < n; i++) if (i != best) free(bufs[i]);
//     *out_len = lens[best];
//     return bufs[best];
// }
pub fn take_largest(buffers: Vec<Vec<u8>>) -> Option<Vec<u8>> {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;

fn main() {
    let big = vec![7u8; 4];
    let big_ptr = big.as_ptr();
    let result = solution::take_largest(vec![vec![1], big, vec![2, 2]]).expect("case 1");
    assert_eq!(result, vec![7, 7, 7, 7], "case 1");
    assert_eq!(result.as_ptr(), big_ptr, "case 2: the buffer must move, not be copied");
    assert_eq!(solution::take_largest(Vec::new()), None, "case 3");
    let first = vec![1u8, 1];
    let first_ptr = first.as_ptr();
    let tie = solution::take_largest(vec![first, vec![2, 2]]).expect("case 4");
    assert_eq!(tie, vec![1, 1], "case 4: the first longest buffer wins a tie");
    assert_eq!(tie.as_ptr(), first_ptr, "case 5");

    println!("PASS c-malloc-free-to-ownership");
}
''',
    "cases": [
        ("visible", "solution::take_largest(vec![vec![1], vec![7; 4], vec![2, 2]])", "Some(vec![7, 7, 7, 7])"),
        ("semantic", "solution::take_largest(..).as_ptr() == big.as_ptr()", "true"),
        ("boundary", "solution::take_largest(Vec::new())", "None"),
        ("boundary", "solution::take_largest(vec![vec![1, 1], vec![2, 2]])", "Some(vec![1, 1])"),
    ],
}

EXPECT = {
    "example": "archived q3-summary\nend of main\ndrop file\ndrop lock\ndrop log\n",
    "practice": {"errors": ["E0382"]},
    "recall": [None, {"errors": ["E0382"]}],
    "probes": {
        "quiz": {"code": "struct Noisy(&'static str);\nimpl Drop for Noisy {\n    fn drop(&mut self) { println!(\"{}\", self.0); }\n}\nfn main() {\n    let _log = Noisy(\"log\");\n    let _lock = Noisy(\"lock\");\n    let _file = Noisy(\"file\");\n}", "stdout": "file\nlock\nlog\n"},
    },
    "c": {"warnings": [], "exit": -5, "sanitize": "address",
          "finding": "attempting double-free"},
    "wrong": {
        "c-malloc-free-to-ownership.1.rs": {"mode": "panic", "note": "copies the winner with `.cloned()`: a second buffer instead of a move"},
        "c-malloc-free-to-ownership.2.rs": {"mode": "panic", "note": "`max_by_key` returns the last of equal maxima, so a tie picks the wrong buffer"},
    },
}
