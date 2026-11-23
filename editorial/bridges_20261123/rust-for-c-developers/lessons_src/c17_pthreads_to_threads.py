ID = "c-pthreads-to-threads"
UNIT = "c-systems"
ORDER = 2

FROM_CODE = r'''#include <pthread.h>
#include <stdio.h>

static long hits = 0;                       /* shared and unprotected */
static long safe_hits = 0;                  /* protected by `lock`, by convention */
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

static void *work(void *arg) {
    (void)arg;
    for (int i = 0; i < 100000; i++) {
        hits++;                             /* data race: TSan reports it */
        pthread_mutex_lock(&lock);
        safe_hits++;
        pthread_mutex_unlock(&lock);        /* an early return here would deadlock */
    }
    return NULL;
}

int main(void) {
    pthread_t t[4];
    for (int i = 0; i < 4; i++) pthread_create(&t[i], NULL, work, NULL);
    for (int i = 0; i < 4; i++) pthread_join(t[i], NULL);
    printf("safe_hits=%ld (hits=%ld may be lower)\n", safe_hits, hits);
    return 0;
}
'''

EXAMPLE = r'''use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let hits = Arc::new(Mutex::new(0u64)); // the Mutex owns the counter
    let mut handles = Vec::new();
    for _ in 0..4 {
        let hits = Arc::clone(&hits);       // one shared owner per thread
        handles.push(thread::spawn(move || { // `move`: the thread owns its Arc
            for _ in 0..100_000 {
                *hits.lock().unwrap() += 1; // the guard drops at `;`: unlocked
            }
        }));
    }
    for handle in handles {
        handle.join().unwrap();
    }
    println!("hits={}", *hits.lock().unwrap());
}
'''

PRACTICE = r'''use std::thread;

fn main() {
    let mut hits = 0u64;
    let handle = thread::spawn(|| {
        hits += 1;
    });
    handle.join().unwrap();
    println!("{hits}");
}
'''

LESSON = {
    "title": "pthreads to std::thread",
    "concept": "Locks that own data, threads that own their captures",
    "minutes": 13,
    "exerciseKind": "planned",
    "writing": {
        "summary": "Rust threads are the same OS threads as pthreads, but a `Mutex` owns the data it protects and the compiler rejects data races.",
        "rule": "`thread::spawn` needs a `Send + 'static` closure, so captures are moved in; shared state goes in `Arc<Mutex<T>>`, and the lock guard unlocks when it drops.",
        "explanation": (
            "With pthreads, the relationship between a mutex and the data it protects is a convention: `lock` guards `safe_hits` because everyone agrees to lock first. Nothing stops the unprotected `hits++`, which ThreadSanitizer reports as a `data race`, and forgetting `pthread_mutex_unlock` on one early return deadlocks the next thread that locks.\n\n"
            "`std::thread::spawn` starts an OS thread and returns a `JoinHandle`; `join()` waits for it and returns the thread's result. The closure must be `'static`, because the thread may outlive the function that spawned it, so borrowing a local is rejected with `E0373`, closure may outlive the current function. `move` makes the closure own its captures instead. When threads only need to borrow locals for a bounded time, `thread::scope` guarantees they are joined before the scope ends and lets them borrow.\n\n"
            "`Mutex<T>` contains the `T`. The only way to reach the value is `lock()`, which returns a guard that dereferences to the data and unlocks when it is dropped, at the end of its statement or block, including on an early return or a panic. `Arc<T>` is an atomically reference-counted pointer, so each thread can own a handle to the same mutex; the non-atomic `Rc<T>` is not `Send`, and the compiler refuses to move it into a thread.\n\n"
            "Those checks come from two marker traits. `Send` means a value can be moved to another thread, and `Sync` means `&T` can be shared between threads. Types implement them automatically when all their fields do, which is how the compiler proves a safe program free of data races. Deadlocks and lock ordering remain your design problem, as in C."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "Each thread owns a clone of the `Arc`, the counter lives inside the `Mutex`, and each guard unlocks at the end of its statement.",
        "practiceCode": PRACTICE,
        "task": "Explain where the quiz program unlocks its mutex and why the closure needs `move`, then fix the practice program with an `Arc<Mutex<u64>>`.",
        "success": "You can point to the statement where each guard drops and explain why a spawned thread cannot borrow a local of `main`.",
        "question": "In `let total = Arc::clone(&total); thread::spawn(move || { let mut n = total.lock().unwrap(); *n += 1; });`, where is the mutex unlocked, and why is `move` needed?",
        "answers": [
            "At `join()`; `move` is optional because `Arc` is thread-safe",
            "Only when `drop(total)` is called; `move` copies the counter into the thread",
            "After the loop that spawns the threads; `move` makes the closure `Copy`",
            "When the guard `n` drops at the end of the closure; `move` gives the thread its own `Arc`, because the thread may outlive the locals of the function that spawned it",
        ],
        "correctAnswer": 3,
        "feedback": "The guard is a local of the closure and unlocks when it goes out of scope. Without `move`, the closure would borrow `total`, and `spawn` requires `'static` captures.",
        "recall": [
            {
                "question": "Why does rustc refuse to move an `Rc<RefCell<u64>>` into `thread::spawn`?",
                "answer": "`Rc` updates its reference count without atomic operations, so two threads cloning or dropping it could corrupt the count. `Rc` is not `Send`, and `spawn` requires a `Send` closure. Use `Arc` for the shared ownership and a `Mutex` or an atomic for the value.",
            },
            {
                "question": "When is `thread::scope` a better fit than `thread::spawn`?",
                "code": "let data = vec![1, 2, 3, 4];\nlet (left, right) = data.split_at(2);\nlet (a, b) = std::thread::scope(|s| {\n    let ha = s.spawn(|| left.iter().sum::<i32>());\n    let hb = s.spawn(|| right.iter().sum::<i32>());\n    (ha.join().unwrap(), hb.join().unwrap())\n});\nprintln!(\"{a} {b}\");",
                "answer": "When threads only need to borrow local data for a bounded time. Scoped threads are joined before `scope` returns, so they may borrow `left` and `right` without `move` or `Arc`; this prints `3 7`.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Find the shared data", "detail": "List what the C threads share, and put each item inside the `Mutex` or atomic that protects it."},
            {"title": "Give each thread an owner", "detail": "Clone the `Arc` once per thread and `move` the clone into that thread's closure."},
            {"title": "Locate the unlock", "detail": "Find where each guard is dropped; keep guards out of slow operations, and never take two locks in different orders."},
        ],
        "misconception": "“A Rust `Mutex` is a separate lock object, like a `pthread_mutex_t` next to the data.”",
        "correction": "`Mutex<T>` wraps the data itself. Code that does not hold a guard has no path to the `T`, so forgetting to lock does not compile, and the guard makes forgetting to unlock impossible.",
        "transferChallenge": "Replace `Mutex<u64>` with `AtomicU64` and `fetch_add(1, Ordering::Relaxed)`, then explain why `Relaxed` is enough for a counter that is read only after every `join`.",
        "connections": [
            {"direction": "previous", "title": "unsafe, Raw Pointers and FFI", "concept": "Where Rust hands the proof back to you"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "`hits` is shared without a lock, which ThreadSanitizer reports as a data race; `safe_hits` is protected only by convention.",
        "contrasts": [
            {"from": "A mutex protects data by convention.",
             "rust": "`Mutex<T>` owns the `T`; the data is reachable only through `lock()`."},
            {"from": "`pthread_mutex_unlock` must run on every path.",
             "rust": "The guard unlocks when it drops, including on early returns."},
            {"from": "Passing `&local` to a thread compiles and may dangle.",
             "rust": "`spawn` needs `'static`; borrowing a local is `E0373`, so use `move` or `thread::scope`."},
        ],
        "credits": ["concurrency/concurrency", "concurrency/shared-state"],
    },
}

EXPECT = {
    "example": "hits=400000\n",
    "practice": {"errors": ["E0373", "E0502"]},
    "recall": [None, {"stdout": "3 7\n"}],
    "probes": {
        "quiz": {"code": "use std::sync::{Arc, Mutex};\nuse std::thread;\nfn main() {\n    let total = Arc::new(Mutex::new(0u64));\n    let mut handles = Vec::new();\n    for _ in 0..4 {\n        let total = Arc::clone(&total);\n        handles.push(thread::spawn(move || {\n            let mut n = total.lock().unwrap();\n            *n += 1;\n        }));\n    }\n    for h in handles { h.join().unwrap(); }\n    println!(\"{}\", *total.lock().unwrap());\n}", "stdout": "4\n"},
        "rc-not-send": {"code": "use std::cell::RefCell;\nuse std::rc::Rc;\nuse std::thread;\nfn main() {\n    let hits = Rc::new(RefCell::new(0u64));\n    let h = Rc::clone(&hits);\n    thread::spawn(move || *h.borrow_mut() += 1).join().unwrap();\n}", "errors": ["E0277"]},
    },
    "c": {"warnings": [], "stdoutPrefix": "safe_hits=400000 ", "exit": 0, "sanitize": "thread",
          "finding": "WARNING: ThreadSanitizer: data race"},
}
