ID = "c-tagged-unions-to-enums"
UNIT = "c-data"
ORDER = 1

FROM_CODE = r'''#include <stdio.h>

enum ev_kind { EV_KEY, EV_CLICK, EV_QUIT };
struct event {
    enum ev_kind kind;                       /* the tag */
    union { char key; struct { int x, y; } click; } as;
};

static void describe(const struct event *e) {
    switch (e->kind) {
    case EV_KEY:   printf("key %c\n", e->as.key); break;
    case EV_CLICK: printf("click at %d,%d\n", e->as.click.x, e->as.click.y); break;
    default:       printf("ignored\n");      /* EV_QUIT and any future kind */
    }
}

int main(void) {
    struct event events[] = {
        {EV_KEY, .as.key = 'q'},
        {EV_CLICK, .as.click = {3, 4}},
        {EV_QUIT, .as.key = 0},
    };
    for (int i = 0; i < 3; i++) describe(&events[i]);
    /* Nothing ties tag to member: {EV_CLICK, .as.key = 'q'} also compiles. */
    return 0;
}
'''

EXAMPLE = r'''enum Event {
    Key(char),
    Click { x: i32, y: i32 },
    Quit,
}

fn describe(event: &Event) -> String {
    match event { // must cover every variant
        Event::Key(c) => format!("key {c}"),
        Event::Click { x, y } if *x < 0 || *y < 0 => "click off-screen".to_string(),
        Event::Click { x, y } => format!("click at {x},{y}"),
        Event::Quit => "quit".to_string(),
    }
}

fn main() {
    let events = [
        Event::Key('q'),
        Event::Click { x: 3, y: 4 },
        Event::Click { x: -1, y: 0 },
        Event::Quit,
    ];
    for event in &events {
        println!("{}", describe(event));
    }
}
'''

PRACTICE = r'''enum Event {
    Key(char),
    Click { x: i32, y: i32 },
    Quit,
}

fn describe(event: &Event) -> String {
    match event {
        Event::Key(c) => format!("key {c}"),
        Event::Click { x, y } if *x >= 0 && *y >= 0 => format!("click at {x},{y}"),
        Event::Quit => "quit".to_string(),
    }
}

fn main() {
    println!("{}", describe(&Event::Quit));
}
'''

LESSON = {
    "title": "Tagged Unions to Enums",
    "concept": "A tag that cannot disagree with its payload",
    "minutes": 12,
    "exerciseKind": "runnable",
    "writing": {
        "summary": "A Rust `enum` is a tagged union whose tag and payload cannot disagree, and `match` must handle every variant.",
        "rule": "`match` must be exhaustive: every variant has to be handled, and an arm with a guard does not count as covering its pattern.",
        "explanation": (
            "The C tagged union is a discipline: an `enum` tag next to a `union`, and every reader checks the tag before touching the matching member. Nothing enforces it. `{EV_CLICK, .as.key = 'q'}` compiles, reading the wrong member is not diagnosed, and a `default:` arm silently absorbs kinds added later, with no `-Wswitch` warning because a default exists.\n\n"
            "A Rust `enum` makes the pairing part of the type. `Key(char)`, `Click { x, y }` and `Quit` are variants, each with its own data, and the only way to reach that data is to match the variant; you cannot build a `Click` that holds a `char`. The compiler chooses the tag and the layout, and uses invalid bit patterns (niches) where it can, which is why `Option<&T>` is the size of a pointer.\n\n"
            "`match` is a `switch` that destructures and is checked for completeness. Leave a variant out and the program does not compile (`E0004`, non-exhaustive patterns), so adding a variant produces a list of every place that must handle it. A `_` arm opts back into C's `default:` behaviour; use it only when new variants really should fall through. Arms never fall through to each other, so there is no `break` to forget.\n\n"
            "Arms can bind fields (`Event::Click { x, y }`), match literals and ranges, and add a guard such as `if *x < 0`. A guard narrows its arm, but exhaustiveness checking ignores guard conditions, so a guarded arm still needs an unguarded arm, or a wildcard, for the same variant. `match` is also an expression whose arms produce one type, which replaces a `switch` that assigns a variable in every case."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "Each variant carries only its own data; the guarded `Click` arm is backed by an unguarded one, and the `match` lists every variant.",
        "practiceCode": PRACTICE,
        "task": "Port the commented C `area`, including the forgotten triangle: return the area rounded down for every variant without overflowing, and make `is_degenerate` return true when any dimension is zero.",
        "success": "`Square { side: u32::MAX }` gives the exact `u64` area, a 3 × 3 triangle gives 4, and zero-sized shapes are degenerate.",
        "question": "In the practice code every variant appears in the `match`. Why does rustc still reject it?",
        "answers": [
            "The `Click` arm has a guard, and guards do not count toward exhaustiveness, so a click with a negative coordinate is unhandled",
            "`match` needs a `default` arm, like a C `switch`",
            "Struct-like variants cannot have guards",
            "`Quit` carries no data, so it must be listed first",
        ],
        "correctAnswer": 0,
        "feedback": "Add an unguarded `Event::Click { .. }` arm after the guarded one. The compiler checks patterns, not the conditions in guards.",
        "recall": [
            {
                "question": "Why is a `_ => ...` arm in a `match` over your own enum often a mistake?",
                "answer": "It turns off the check that makes enums safer than a C `switch`: a variant added later falls into `_` silently instead of producing `E0004` at every `match` that must handle it. List the variants unless falling through really is the intended behaviour.",
            },
            {
                "question": "What does this print?",
                "code": "enum Size { Small, Large(u32) }\nfn main() {\n    let sizes = [Size::Small, Size::Large(3), Size::Large(12)];\n    for s in &sizes {\n        let label = match s {\n            Size::Small => \"small\",\n            Size::Large(n) if *n > 10 => \"huge\",\n            Size::Large(_) => \"large\",\n        };\n        print!(\"{label} \");\n    }\n}",
                "answer": "`small large huge`. Arms are tried in order: `Large(3)` fails the guard and reaches the unguarded `Large(_)` arm, while `Large(12)` matches the guarded arm first.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Map the tags", "detail": "Turn each C tag value into a variant, and move the union member it selects into that variant."},
            {"title": "Delete the default", "detail": "Replace `default:` with explicit variants, compile, and handle every place that `E0004` reports."},
            {"title": "Back each guard", "detail": "For every guarded arm, make sure an unguarded arm for the same variant follows it."},
        ],
        "misconception": "“A Rust enum is a C `enum` with extra syntax.”",
        "correction": "A C `enum` is a set of integer constants. A Rust `enum` is a sum type: each variant can carry its own fields, and the compiler stores and checks the tag. Fieldless variants can still be given C-style integer values, with `#[repr(...)]` when the representation matters.",
        "transferChallenge": "Add a `Circle { r: u32 }` variant to `Shape` and let the compiler list every `match` to update; then decide how `area` should round it.",
        "connections": [
            {"direction": "previous", "title": "Structs and Methods", "concept": "The receiver states the pointer contract"},
            {"direction": "next", "title": "NULL and errno to Option and Result", "concept": "Absence and failure in the return type"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "The tag and the union member are kept in sync by hand, and `default:` absorbs any kind added later.",
        "contrasts": [
            {"from": "Tag and union member can disagree; nothing checks the pairing.",
             "rust": "A variant and its data are one value; the data is reached only by matching."},
            {"from": "`default:` silently handles kinds added later.",
             "rust": "A missing variant is error `E0004`; `_` is an explicit opt-in."},
            {"from": "Cases fall through unless you write `break`.",
             "rust": "Arms never fall through, and each `match` arm is an expression."},
        ],
        "credits": ["basics/enums", "basics/pattern-matching"],
    },
}

CHALLENGE = {
    "functions": ["area", "is_degenerate"],
    "source": r'''// C original:
// enum kind { SQUARE, RECT, TRIANGLE };
// struct shape { enum kind kind; uint32_t a, b; };
// uint64_t area(const struct shape *s) {
//     switch (s->kind) {
//     case SQUARE: return s->a * s->a;          /* 32-bit multiply, then widened */
//     case RECT:   return (uint64_t)s->a * s->b;
//     default:     return 0;                    /* TRIANGLE was forgotten */
//     }
// }
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Shape {
    Square { side: u32 },
    Rect { w: u32, h: u32 },
    Triangle { base: u32, height: u32 },
}

/// The area, rounded down.
pub fn area(shape: &Shape) -> u64 {
    todo!("implement the contract")
}

/// True when any dimension is zero.
pub fn is_degenerate(shape: &Shape) -> bool {
    todo!("implement the contract")
}
''',
    "harness": r'''mod solution;
use solution::Shape;

fn main() {
    assert_eq!(solution::area(&Shape::Square { side: 3 }), 9, "case 1");
    assert_eq!(solution::area(&Shape::Rect { w: 2, h: 5 }), 10, "case 2");
    assert_eq!(solution::area(&Shape::Triangle { base: 3, height: 3 }), 4, "case 3");
    assert_eq!(solution::area(&Shape::Square { side: u32::MAX }), 18_446_744_065_119_617_025, "case 4");
    assert_eq!(solution::area(&Shape::Triangle { base: u32::MAX, height: u32::MAX }), 9_223_372_032_559_808_512, "case 5");
    assert!(solution::is_degenerate(&Shape::Rect { w: 0, h: 5 }), "case 6");
    assert!(solution::is_degenerate(&Shape::Triangle { base: 4, height: 0 }), "case 7");
    assert!(!solution::is_degenerate(&Shape::Square { side: 1 }), "case 8");

    println!("PASS c-tagged-unions-to-enums");
}
''',
    "cases": [
        ("visible", "solution::area(&Shape::Square { side: 3 })", "9"),
        ("visible", "solution::area(&Shape::Rect { w: 2, h: 5 })", "10"),
        ("semantic", "solution::area(&Shape::Triangle { base: 3, height: 3 })", "4"),
        ("boundary", "solution::area(&Shape::Square { side: u32::MAX })", "18446744065119617025"),
        ("boundary", "solution::area(&Shape::Triangle { base: u32::MAX, height: u32::MAX })", "9223372032559808512"),
        ("semantic", "solution::is_degenerate(&Shape::Rect { w: 0, h: 5 })", "true"),
        ("semantic", "solution::is_degenerate(&Shape::Triangle { base: 4, height: 0 })", "true"),
        ("boundary", "solution::is_degenerate(&Shape::Square { side: 1 })", "false"),
    ],
}

EXPECT = {
    "example": "key q\nclick at 3,4\nclick off-screen\nquit\n",
    "practice": {"errors": ["E0004"]},
    "recall": [None, {"stdout": "small large huge "}],
    "c": {"warnings": [], "stdout": "key q\nclick at 3,4\nignored\n", "exit": 0},
    "wrong": {
        "c-tagged-unions-to-enums.1.rs": {"mode": "panic", "note": "C habit: multiply in 32 bits and widen afterwards, `(side * side) as u64`"},
        "c-tagged-unions-to-enums.2.rs": {"mode": "panic", "note": "keeps the C `default: return 0` as `_ => 0`, so triangles have no area"},
    },
}
