ID = "c-structs-to-impl"
UNIT = "c-data"
ORDER = 0

FROM_CODE = r'''#include <stdio.h>

struct counter { const char *label; unsigned hits; };

void counter_hit(struct counter *c) { c->hits++; }                 /* may modify */
unsigned counter_hits(const struct counter *c) { return c->hits; } /* reads only */
unsigned counter_finish(struct counter *c) {      /* "do not use c after this" */
    unsigned n = c->hits;
    c->label = NULL;
    return n;
}

int main(void) {
    struct counter c = {"visits", 0};
    counter_hit(&c);
    counter_hit(&c);
    printf("%s: %u\n", c.label, counter_hits(&c));
    printf("final: %u\n", counter_finish(&c));
    counter_hit(&c);   /* compiles: the contract lived in a comment */
    return 0;
}
'''

EXAMPLE = r'''struct Counter {
    label: String,
    hits: u32,
}

impl Counter {
    fn new(label: &str) -> Self { // an associated function, like counter_init
        Counter { label: label.to_string(), hits: 0 }
    }
    fn hit(&mut self) { self.hits += 1 }          // exclusive access
    fn hits(&self) -> u32 { self.hits }           // shared, read-only access
    fn finish(self) -> (String, u32) {            // takes the value itself
        (self.label, self.hits)
    }
}

fn main() {
    let mut c = Counter::new("visits");
    c.hit(); // auto-borrows: Counter::hit(&mut c)
    c.hit();
    println!("{}: {}", c.label, c.hits());
    let (label, total) = c.finish(); // `c` is moved: no use after this
    println!("final {label}: {total}");
}
'''

PRACTICE = r'''struct Counter {
    hits: u32,
}

impl Counter {
    fn hit(&mut self) { self.hits += 1 }
    fn finish(self) -> u32 { self.hits }
}

fn main() {
    let mut c = Counter { hits: 0 };
    c.hit();
    let total = c.finish();
    c.hit();
    println!("{total}");
}
'''

LESSON = {
    "title": "Structs and Methods",
    "concept": "The receiver states the pointer contract",
    "minutes": 12,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "Methods live in an `impl` block, and the receiver (`&self`, `&mut self` or `self`) states what C expressed with `const` pointers and comments.",
        "rule": "`&self` reads, `&mut self` modifies, and `self` consumes the value; read a method's receiver to learn its ownership effect.",
        "explanation": (
            "C groups behaviour by naming convention: `counter_hit(struct counter *)`, `counter_hits(const struct counter *)` and `counter_finish(...)`, with a comment that says not to use the counter afterwards. The `const` documents read-only access, and the do-not-use-after rule is not checked at all: the example calls `counter_hit` after `counter_finish`, and it compiles.\n\n"
            "In Rust, functions associated with a type go in `impl Counter { ... }`. The receiver is the first parameter and carries the contract. `fn hits(&self)` is a shared borrow, like a `const` pointer with the stronger guarantee that nobody mutates the value during the call. `fn hit(&mut self)` is an exclusive borrow. `fn finish(self)` takes the value itself: after `c.finish()`, `c` has moved, and calling `c.hit()` is error `E0382`.\n\n"
            "Method calls borrow automatically: `c.hit()` means `Counter::hit(&mut c)`, so there is no `&` at the call site and no `->` operator; `.` works through references. A function without a receiver, such as `Counter::new`, is an associated function, the idiomatic replacement for `counter_init`, and it returns the initialised value instead of filling memory the caller provides.\n\n"
            "Fields are private to the module unless marked `pub`, so the invariants behind methods such as `spend` and `remaining` can only be broken by code inside that module. That replaces the opaque-pointer pattern, `struct budget;` in the header, for most C APIs."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "`hit` takes `&mut self`, `hits` takes `&self`, and `finish` takes `self`, so the counter cannot be used after it.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C budget: `spend` refuses an amount larger than what remains and then changes nothing, `remaining` reports the rest, and `close` consumes the budget and returns the amount spent. Avoid the C version's wrapping sum.",
        "success": "Spending exactly the remainder succeeds, a refused spend leaves the state unchanged, and `spend(u32::MAX)` is refused without overflowing.",
        "question": "Which receiver should `close` take so that using the budget after `budget.close()` is a compile error?",
        "answers": [
            "`&self`",
            "`self`",
            "`&mut self`",
            "`&'static self`",
        ],
        "correctAnswer": 1,
        "feedback": "`self` moves the value into the method. The caller's binding has moved, so any later method call on it is `E0382`.",
        "recall": [
            {
                "question": "Which receivers match these C prototypes: `size_t buf_len(const struct buf *)`, `void buf_push(struct buf *, uint8_t)` and `uint8_t *buf_into_raw(struct buf *)`, after which the buffer must not be used?",
                "answer": "`fn len(&self) -> usize`, `fn push(&mut self, byte: u8)` and `fn into_raw(self) -> ...`. The `into_` prefix is the Rust naming convention for a method that consumes `self`.",
            },
            {
                "question": "Why is `budget.spend(5)` allowed on `let mut budget` but not on `let budget`?",
                "answer": "`spend` takes `&mut self`, so the call borrows `budget` mutably, and that needs a `mut` binding. `remaining(&self)` works on either.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Read the receivers", "detail": "For each method, note `&self`, `&mut self` or `self` before reading its body."},
            {"title": "Mark the consuming calls", "detail": "After a call to a `self` method, the receiver binding has moved; check that nothing uses it later."},
            {"title": "Check the invariant", "detail": "Keep fields private so only the module's methods can change them, then test each method at its boundary."},
        ],
        "misconception": "“`self` in Rust is like `this` in C++: always a pointer.”",
        "correction": "`self` by value is the whole struct moved into the method; `&self` and `&mut self` are the borrowed forms. The receiver is chosen per method and is part of the API contract.",
        "transferChallenge": "Add `fn reset(&mut self)` and `fn split(self, part: u32) -> (Budget, Budget)` to `Budget`, then predict which later calls compile after each one.",
        "connections": [
            {"direction": "previous", "title": "Struct Copies: Copy and Clone", "concept": "Bitwise copies only for plain data"},
            {"direction": "next", "title": "Tagged Unions to Enums", "concept": "A tag that cannot disagree with its payload"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "The receiver contract is a naming convention plus `const`; using the counter after `counter_finish` compiles.",
        "contrasts": [
            {"from": "`const struct counter *` documents read-only access.",
             "rust": "`&self` is a shared borrow; no one mutates the value during the call."},
            {"from": "Do not use the counter after `counter_finish` is a comment.",
             "rust": "`fn finish(self)` consumes the value; a later use is `E0382`."},
            {"from": "`counter_init(&c)` fills memory the caller provides.",
             "rust": "`Counter::new()` returns an initialised value; `c.hit()` borrows automatically."},
        ],
        "credits": ["basics/structs", "basics/methods-intro"],
    },
}

CHALLENGE = {
    "functions": ["new", "spend", "remaining", "close"],
    "source": r'''// C original:
// struct budget { unsigned limit, spent; };
// unsigned budget_remaining(const struct budget *b) { return b->limit - b->spent; }
// int budget_spend(struct budget *b, unsigned amount) {
//     if (b->spent + amount > b->limit) return -1;  /* the sum can wrap */
//     b->spent += amount;
//     return 0;
// }
// unsigned budget_close(struct budget b) { return b.spent; }
pub struct Budget {
    limit: u32,
    spent: u32,
}

impl Budget {
    pub fn new(limit: u32) -> Self {
        todo!("implement the contract")
    }

    pub fn spend(&mut self, amount: u32) -> bool {
        todo!("implement the contract")
    }

    pub fn remaining(&self) -> u32 {
        todo!("implement the contract")
    }

    pub fn close(self) -> u32 {
        todo!("implement the contract")
    }
}
''',
    "harness": r'''mod solution;
use solution::Budget;

fn main() {
    let mut b = Budget::new(100);
    assert!(b.spend(30), "case 1");
    assert_eq!(b.remaining(), 70, "case 2");
    assert!(!b.spend(80), "case 3: refused");
    assert_eq!(b.remaining(), 70, "case 4: a refused spend changes nothing");
    assert!(!b.spend(u32::MAX), "case 5: no wrapping sum");
    assert!(b.spend(70), "case 6: exactly the remainder");
    assert_eq!(b.remaining(), 0, "case 7");
    assert_eq!(b.close(), 100, "case 8");

    println!("PASS c-structs-to-impl");
}
''',
    "cases": [
        ("visible", "Budget::new(100).spend(30)", "true"),
        ("semantic", "remaining() after spending 30", "70"),
        ("semantic", "spend(80) with 70 remaining, then remaining()", "false, 70"),
        ("boundary", "spend(u32::MAX)", "false"),
        ("boundary", "spend(70) with 70 remaining, then remaining()", "true, 0"),
        ("visible", "close()", "100"),
    ],
}

EXPECT = {
    "example": "visits: 2\nfinal visits: 2\n",
    "practice": {"errors": ["E0382"]},
    "recall": [None, None],
    "probes": {
        "quiz-borrowed-close": {"code": "struct Budget { spent: u32 }\nimpl Budget {\n    fn close(&self) -> u32 { self.spent }\n}\nfn main() {\n    let b = Budget { spent: 3 };\n    let total = b.close();\n    println!(\"{total} {}\", b.close());\n}", "stdout": "3 3\n"},
        "immutable-binding": {"code": "struct Budget { spent: u32 }\nimpl Budget {\n    fn spend(&mut self, amount: u32) { self.spent += amount; }\n}\nfn main() {\n    let budget = Budget { spent: 0 };\n    budget.spend(5);\n}", "errors": ["E0596"]},
    },
    "c": {"warnings": [], "stdout": "visits: 2\nfinal: 2\n", "exit": 0},
    "wrong": {
        "c-structs-to-impl.1.rs": {"mode": "panic", "note": "C original's `spent + amount > limit`: overflows on `u32::MAX` (a panic in debug, a wrapped sum in release)"},
    },
}
