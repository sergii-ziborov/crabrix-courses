"""Unit node-values: values and types. Authored source for author.py."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


LESSONS = []

# ---------------------------------------------------------------- 1
LESSONS.append(dict(
    id="node-console-log-to-println",
    unit="node-values",
    title="console.log vs println!",
    concept="Compile-time checked formatting",
    minutes=9,
    kind="runnable",
    summary="`println!` replaces `console.log`, and rustc checks every placeholder against its arguments before the program runs.",
    rule="Execution starts in `fn main()`; `println!` and `format!` are macros whose placeholders are checked during compilation.",
    explanation=[
        "A Node.js module runs from top to bottom, so `console.log` can sit anywhere at the top level. A Rust binary has no top-level statements: execution starts in `fn main()`, and everything else is an item, such as a function, a struct or a `use` declaration, that runs only when `main` calls it.",
        "`println!` is a macro, not a function; the `!` marks the call. It expands during compilation, so rustc checks the format string against the arguments before the program exists. A missing argument is a compile error, not a stray `%d` in the output as with `console.log(\"%s costs %d cents\", \"tea\")`. `format!` builds the same text as a `String` instead of printing it, which is the job a template literal does in JavaScript.",
        "Placeholders replace interpolation. `{}` formats with the `Display` trait, `{name}` captures a variable that is in scope, and `{:?}` formats with `Debug`. Format options cover what you used `padStart` and `toFixed` for: `{rest:02}` pads with zeros to width 2, `{:<8}` left-aligns in 8 columns and `{:.2}` prints two decimals. `console.log` inspects any object; a Rust type prints with `{:?}` only if it implements `Debug`, usually through `#[derive(Debug)]`.",
        "`println!` writes to stdout and `eprintln!` to stderr, the counterparts of `console.log` and `console.error`. Neither is a way to hand data back from a function. Return a `String` and let the caller decide where it goes, which is also what makes the lab's `clock` function testable.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        function receiptLine(item, qty, cents) {
          const dollars = Math.floor(cents / 100);
          const rest = String(cents % 100).padStart(2, "0");
          return `${item} x${qty} = $${dollars}.${rest}`;
        }

        console.log(receiptLine("tea", 2, 705));
        console.log(receiptLine("mint", 1, 5));
        console.log("%s costs %d cents", "tea");
    '''),
    from_stdout="tea x2 = $7.05\nmint x1 = $0.05\ntea costs %d cents\n",
    from_caption="A template literal builds the line, and `console.log` checks nothing: the last call prints a literal `%d`.",
    example=code(r'''
        fn receipt_line(item: &str, qty: u32, cents: u32) -> String {
            let dollars = cents / 100;
            let rest = cents % 100;
            format!("{item} x{qty} = ${dollars}.{rest:02}")
        }

        fn main() {
            println!("{}", receipt_line("tea", 2, 705));
            println!("{}", receipt_line("mint", 1, 5));
            println!("{:?}", ("tea", 705));
        }
    '''),
    example_stdout="tea x2 = $7.05\nmint x1 = $0.05\n(\"tea\", 705)\n",
    example_caption="`{rest:02}` does the work of `padStart(2, \"0\")`, and `{:?}` prints a value through `Debug`.",
    contrasts=[
        ("`console.log(\"%s costs %d cents\", \"tea\")` prints `tea costs %d cents`.",
         "`println!(\"{} costs {} cents\", item)` does not compile: the format string needs two arguments."),
        ("A module's top-level statements run when it loads.",
         "A binary starts in `fn main()`; other code runs only when it is called."),
        ("`console.log(obj)` inspects any object.",
         "`{:?}` needs a `Debug` implementation, usually `#[derive(Debug)]`."),
        ("`String(n).padStart(2, \"0\")`", "`format!(\"{n:02}\")`"),
    ],
    credits=["basics/hello-rust", "basics/print-formatting"],
    practice=code(r'''
        fn main() {
            let item = "tea";
            println!("{} costs {} cents", item);
        }
    '''),
    practice_expect={"errors": [], "messages": ["2 positional arguments in format string, but there is 1 argument"]},
    question="When does rustc report that `println!(\"{} costs {} cents\", item)` is missing an argument?",
    answers=[
        "When that line runs, like a `TypeError`",
        "During compilation, while the macro expands",
        "Never: the extra placeholder prints literally, as with `console.log`",
    ],
    correct=1,
    feedback="The format string is checked while `println!` expands, so a program with the mismatch is never built.",
    task="Port the JavaScript `clock` shown at the top of solution.rs: whole seconds become `minutes:seconds`, with the seconds always two digits (`125` becomes `2:05`). Return the `String`; do not print it. In the Crabrix app, open the compiler lab and complete the supplied function in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including `0` and single-digit seconds. Printing a success message alone does not complete this lab.",
    misconception="“`println!` is Rust's `console.log`: it formats whatever it is given at runtime.”",
    correction="`println!` is a macro that rustc expands and checks at compile time. Placeholders must match the arguments, and each argument must implement the trait its placeholder asks for: `Display` for `{}`, `Debug` for `{:?}`.",
    trace=[
        ("Find the entry point", "There is no top-level code. `main` calls `receipt_line` twice and prints each returned `String` with `{}`."),
        ("Read the placeholders", "`{item}` and `{qty}` capture variables by name. `${dollars}` is a literal `$` followed by the `{dollars}` placeholder, and `{rest:02}` pads `5` to `05`."),
        ("Compare with evidence", "Run it: `tea x2 = $7.05`, `mint x1 = $0.05`, then `(\"tea\", 705)` from `{:?}` on a tuple. Remove `:02` and the second line becomes `$0.5`."),
    ],
    transfer="Add `#[derive(Debug)] struct Line { item: String, cents: u32 }`, print one value with `{:?}` and then with `{:#?}`. Delete the derive and read which trait rustc says is missing.",
    connections=[("next", "const and let vs let and let mut", "Immutable bindings, mut and shadowing")],
    recall=[
        dict(question="Why does this not compile, and what are two fixes?",
             code=code(r'''
                 let item = "tea";
                 println!("{} costs {} cents", item);
             '''),
             answer="The format string has two `{}` placeholders but only one argument, and `println!` checks that during compilation. Pass a second argument, as in `println!(\"{} costs {} cents\", item, 705)`, or remove the second placeholder.",
             expect={"errors": [], "messages": ["2 positional arguments in format string, but there is 1 argument"]}),
        dict(question="What do `{}`, `{name}` and `{:?}` each require from the value?",
             answer="`{}` requires `Display`, the user-facing format. `{name}` is the same `{}` placeholder, capturing the variable `name` from the surrounding scope. `{:?}` requires `Debug`, the developer format most types get from `#[derive(Debug)]`. Unlike `console.log`, nothing is inspected automatically."),
    ],
    challenge=dict(
        function="clock",
        starter=code(r'''
            // JavaScript original:
            // function clock(totalSeconds) {
            //   const m = Math.floor(totalSeconds / 60);
            //   const s = String(totalSeconds % 60).padStart(2, "0");
            //   return `${m}:${s}`;
            // }
            pub fn clock(total_seconds: u32) -> String {
                todo!("implement the contract")
            }
        '''),
        cases=[
            ("visible", "solution::clock(125)", "\"2:05\""),
            ("boundary", "solution::clock(0)", "\"0:00\""),
            ("semantic", "solution::clock(59)", "\"0:59\""),
            ("semantic", "solution::clock(600)", "\"10:00\""),
            ("boundary", "solution::clock(3599)", "\"59:59\""),
        ],
        solution=code(r'''
            pub fn clock(total_seconds: u32) -> String {
                format!("{}:{:02}", total_seconds / 60, total_seconds % 60)
            }
        '''),
        wrong=[
            ("seconds without zero padding", code(r'''
                pub fn clock(total_seconds: u32) -> String {
                    format!("{}:{}", total_seconds / 60, total_seconds % 60)
                }
            ''')),
        ],
        js_lang="javascript",
        js_original=code(r'''
            function clock(totalSeconds) {
              const m = Math.floor(totalSeconds / 60);
              const s = String(totalSeconds % 60).padStart(2, "0");
              return `${m}:${s}`;
            }
        '''),
        js_checks=[("clock(125)", "2:05"), ("clock(0)", "0:00"), ("clock(59)", "0:59"),
                   ("clock(600)", "10:00"), ("clock(3599)", "59:59")],
    ),
))

# ---------------------------------------------------------------- 2
LESSONS.append(dict(
    id="node-let-const-to-let-mut",
    unit="node-values",
    title="const and let vs let and let mut",
    concept="Immutable bindings, mut and shadowing",
    minutes=8,
    kind="planned",
    summary="Rust's plain `let` is stricter than `const`: without `mut` you can neither reassign the binding nor change the value through it.",
    rule="`let` is immutable, `let mut` permits change, and a new `let` with the same name shadows the old binding.",
    explanation=[
        "In JavaScript, `const` protects the binding, not the value: `const tags = []` can still `push`. Rust's `let` protects both. Without `mut` you cannot assign a new value, and you cannot call a method that needs `&mut self`, such as `Vec::push`. `let mut` is the explicit opt-in, so a reader finds every binding that changes by scanning for `mut`.",
        "Rust also has `const`, but it means something else: a compile-time constant with a mandatory type, such as `const MAX_RETRIES: u32 = 3;`, which may live at module level. It is closer to a named literal that the compiler inlines than to a JavaScript `const` binding.",
        "Shadowing replaces the common `let input = ...; input = Number(input)` pattern. A second `let input` declares a new binding that hides the first one for the rest of the scope, and it may have a different type, so `let input: i32 = input.trim().parse()?` turns text into a number without inventing `inputText` and `inputNumber`. The old value is not mutated; it is simply no longer reachable by that name. In JavaScript, declaring `let input` twice in one scope is a `SyntaxError`.",
        "Mutability belongs to the binding, not to the type. Moving a value into a `let mut` binding makes it mutable there, and lending it out as `&mut` requires the owner to be `mut`. That is why the error for the practice code points at the declaration and suggests `let mut tags`.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        const tags = [];
        tags.push("rust");          // allowed: const stops rebinding, not mutation
        let count = tags.length;
        count += 1;

        let input = "  42 ";
        input = Number(input.trim()); // same name, now a number
        console.log(tags, count, input + 1);
    '''),
    from_stdout="[ 'rust' ] 2 43\n",
    from_caption="`const` only stops rebinding, so the array still changes, and `input` turns from a string into a number under the same name.",
    example=code(r'''
        fn main() {
            let mut tags = Vec::new();
            tags.push("rust");
            let mut count = tags.len();
            count += 1;

            let input = "  42 ";
            let input: i32 = input.trim().parse().expect("a literal number");
            println!("{tags:?} {count} {}", input + 1);
        }
    '''),
    example_stdout="[\"rust\"] 2 43\n",
    example_caption="`mut` marks what changes, and the second `let input` shadows the text with an `i32`.",
    contrasts=[
        ("`const tags = []; tags.push(\"rust\")` is allowed.",
         "`let tags = Vec::new(); tags.push(\"rust\")` is E0596; declare `let mut tags`."),
        ("`let count = 1; count += 1` reassigns.",
         "`count += 1` needs `let mut count`; plain `let` rejects the second assignment with E0384."),
        ("Redeclaring `let input` in the same scope is a `SyntaxError`.",
         "`let input = input.trim();` shadows: a new binding, possibly of a new type."),
        ("`const` is a runtime binding.",
         "Rust's `const` is a typed compile-time constant, such as `const MAX: u32 = 3;`."),
    ],
    credits=["basics/variables"],
    practice=code(r'''
        fn main() {
            let tags = Vec::new();
            tags.push("rust");
            println!("{tags:?}");
        }
    '''),
    practice_expect={"errors": ["E0596"]},
    question="Which statement about `let tags = Vec::new(); tags.push(\"rust\");` is true?",
    answers=[
        "It compiles, but the push panics because the vector is frozen",
        "It compiles, exactly like `const tags = []; tags.push(\"rust\")`",
        "rustc rejects the push: without `mut`, the binding cannot be used to change the vector",
    ],
    correct=2,
    feedback="`push` takes `&mut self`, and a binding declared without `mut` cannot lend that out. rustc reports E0596 at compile time.",
    task="Fix the practice code with one keyword, then add `let tags = tags.len();` after the push and print it. Explain why that shadowing line compiles even though `tags` was a `Vec` a moment earlier.",
    success="You can tell which bindings change by reading the `let` lines alone, and you predicted E0596 before compiling.",
    misconception="“Plain `let` is like `const`: the binding is fixed, but the vector inside can still change.”",
    correction="A binding without `mut` cannot change its value at all, including through methods that take `&mut self`. Declare `let mut tags`; types such as `RefCell` that allow change behind a shared reference are a separate, explicit tool.",
    trace=[
        ("Read the bindings", "`tags` and `count` are `let mut` because they change. `input` is never mutated: it is declared twice."),
        ("Follow the shadow", "The second `let input: i32` reads the first `input`, a `&str`, on its right-hand side and then hides it. From that line on, `input` is an `i32`."),
        ("Compare with evidence", "Run it: `[\"rust\"] 2 43`. Remove `mut` from `tags` and rustc reports E0596 at the `push`, pointing at the declaration."),
    ],
    transfer="Write `let x = 5; let x = x * 2; { let x = \"inner\"; println!(\"{x}\"); } println!(\"{x}\");` and predict both lines before running it. Then replace the second `let x = x * 2` with `x = x * 2` and read the error.",
    connections=[("previous", "console.log vs println!", "Compile-time checked formatting"),
                 ("next", "Number vs Rust integer types", "Explicit numeric types and overflow")],
    recall=[
        dict(question="Why is the second line rejected, and what does rustc suggest?",
             code=code(r'''
                 let count = 1;
                 count += 1;
             '''),
             answer="`count` was declared without `mut`, so it cannot be assigned a second time: E0384. rustc suggests `let mut count = 1;`. Plain `let` behaves like a `const` binding whose value also cannot change.",
             expect={"errors": ["E0384"]}),
        dict(question="How is `let input = input.trim();` different from `input = input.trim();` on a `let mut input`?",
             answer="The first declares a new binding that shadows the old one; it may have a different type, and the original binding is left untouched. The second assigns into the same mutable binding, so the new value must have the same type as the old one."),
    ],
))

# ---------------------------------------------------------------- 3
LESSONS.append(dict(
    id="node-number-to-integer-types",
    unit="node-values",
    title="Number vs Rust integer types",
    concept="Explicit numeric types and overflow",
    minutes=12,
    kind="runnable",
    summary="Every JavaScript `Number` is an f64. Rust makes you pick a numeric type, convert between types explicitly and decide what happens on overflow.",
    rule="Numeric types never mix implicitly: convert with `From` or `try_from`, and choose checked, wrapping or saturating arithmetic where overflow is possible.",
    explanation=[
        "JavaScript has one `Number`, an IEEE 754 double. Integers are exact only up to `Number.MAX_SAFE_INTEGER` (2^53 − 1), `0.1 + 0.2 === 0.3` is `false`, and the bitwise operators quietly convert to 32-bit integers. `BigInt` exists but does not mix with `Number`. Rust has fixed-size integers from `i8` to `i128` and `u8` to `u128`, the pointer-sized `usize` and `isize`, and `f32` and `f64`. Floating point behaves as it does in JavaScript; integers are where your habits need to change.",
        "Rust never converts between numeric types for you. `u16 + i32` does not compile, even when every value would fit. Lossless widening is `i32::from(stock)` or `.into()`. Narrowing that may fail is `u16::try_from(n)`, which returns a `Result`. `as` converts too, but it truncates or wraps silently, so keep it for casts you have proved safe.",
        "Overflow is a decision, not an accident. In a debug build, `u32` arithmetic that leaves the range panics with `attempt to subtract with overflow`; in a release build it wraps unless `overflow-checks` is enabled. Neither gives JavaScript's `-2`. When the boundary is part of the contract, say so: `checked_sub` returns `None`, `saturating_sub` stops at `0` and `wrapping_sub` wraps on purpose.",
        "Choose types from the domain. Counts and lengths are usually `usize` or `u32`, money is an integer number of cents rather than an `f64`, and a value that can be negative needs a signed type. The lab's `seats_left` shows why the choice matters: a `u32` has no negative answer, so the function returns `Option<u32>` and the caller handles the overbooked case.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        function applyAdjustment(stock, delta) {
          const next = stock + delta;
          if (!Number.isInteger(next) || next < 0 || next > 65535) return null;
          return next;
        }

        console.log(applyAdjustment(10, -3));
        console.log(applyAdjustment(2, -5));
        console.log(0.1 + 0.2 === 0.3);           // every Number is an f64
        console.log(Number.MAX_SAFE_INTEGER + 2); // 9007199254740992, not ...993
    '''),
    from_stdout="7\nnull\nfalse\n9007199254740992\n",
    from_caption="One `Number` type: the range check is manual, and the last two lines show f64 rounding.",
    example=code(r'''
        fn apply_adjustment(stock: u16, delta: i32) -> Option<u16> {
            let next = i32::from(stock).checked_add(delta)?;
            u16::try_from(next).ok()
        }

        fn main() {
            println!("{:?}", apply_adjustment(10, -3));
            println!("{:?}", apply_adjustment(2, -5));
            println!("{:?}", apply_adjustment(1, i32::MAX));
            println!("{}", 0.1_f64 + 0.2 == 0.3);
            println!("{:?} {}", 200_u8.checked_add(100), 200_u8.wrapping_add(100));
        }
    '''),
    example_stdout="Some(7)\nNone\nNone\nfalse\nNone 44\n",
    example_caption="Widen with `i32::from`, add with `checked_add`, narrow with `u16::try_from`: every boundary is visible.",
    contrasts=[
        ("`stock + delta` works for any two Numbers.",
         "`stock + delta` with a `u16` and an `i32` is a type error; widen first with `i32::from(stock)`."),
        ("`3 - 5` is `-2`.",
         "`u32` values 3 minus 5 panic in a debug build and wrap in release; `3_u32.checked_sub(5)` is `None`."),
        ("Integers above 2^53 − 1 silently lose precision.",
         "`u64` and `i64` are exact over their whole range; leaving it is an explicit overflow case."),
        ("`n | 0` truncates through int32.",
         "`as` also truncates silently; prefer `try_from` when a value might not fit."),
    ],
    credits=["basics/number-types", "basics/operators"],
    practice=code(r'''
        fn main() {
            let stock: u16 = 10;
            let delta: i32 = -3;
            let next = stock + delta;
            println!("{next}");
        }
    '''),
    practice_expect={"errors": ["E0308", "E0277"]},
    question="`fn left(capacity: u32, booked: u32) -> u32 { capacity - booked }` is called with `3` and `5` in a debug build. What happens?",
    answers=[
        "It panics with `attempt to subtract with overflow`",
        "It returns `-2`, as in JavaScript",
        "It returns `0`, because unsigned values saturate",
    ],
    correct=0,
    feedback="Debug builds check integer overflow and panic. A release build would wrap to `4294967294` unless overflow checks are enabled; use `checked_sub` when the boundary is expected.",
    task="Port the JavaScript `seatsLeft` shown at the top of solution.rs. Return `Some(left)` when the capacity covers `booked` plus `requested`, otherwise `None`, and never panic or wrap, whatever `u32` values arrive. In the Crabrix app, open the compiler lab and complete the supplied function in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including exact capacity and bookings beyond `u32::MAX`. Printing a success message alone does not complete this lab.",
    misconception="“An unsigned subtraction below zero just gives a negative number, as in JavaScript.”",
    correction="A `u32` has no negative values. Leaving the range panics in debug builds and wraps in release builds unless overflow checks are on; `checked_sub` turns the boundary into `None`.",
    trace=[
        ("Read the types", "`stock` is a `u16` and `delta` an `i32`. They cannot be added directly, so `i32::from(stock)` widens the stock without loss."),
        ("Follow each boundary", "`checked_add` returns `None` if the sum leaves `i32`, and `?` returns that `None` early. `u16::try_from(next).ok()` turns a negative or too-large result into `None`."),
        ("Compare with evidence", "Run it: `Some(7)`, `None`, `None`, `false`, then `None 44`. The third call adds `i32::MAX` and would panic in a debug build without `checked_add`."),
    ],
    transfer="Replace `checked_add(delta)?` with `+ delta` and call `apply_adjustment(1, i32::MAX)` in a debug build. Rebuild with `rustc -O` and compare. Then try `saturating_add` and decide which behaviour fits a stock counter.",
    connections=[("previous", "const and let vs let and let mut", "Immutable bindings, mut and shadowing"),
                 ("next", "JavaScript functions vs fn", "Typed parameters and tail expressions")],
    recall=[
        dict(question="Why does this compile, and what does it print?",
             code=code(r'''
                 let big: i32 = 300;
                 let n = big as u8;
                 println!("{n} {:?}", u8::try_from(big).is_err());
             '''),
             answer="`as` between integer types never fails: it keeps the low 8 bits, so `300` becomes `44`. `u8::try_from(300)` returns an `Err` instead of a silently different number, so the line prints `44 true`. Prefer `try_from` when a value might not fit.",
             expect={"stdout": "44 true\n"}),
        dict(question="In JavaScript, `2 ** 53 + 1 === 2 ** 53` is `true`. What happens with `u64` in Rust?",
             answer="`u64` represents every integer from 0 to 2^64 − 1 exactly, so `2_u64.pow(53) + 1` is a different value from `2_u64.pow(53)`. Precision loss is a floating-point property. With integers the only boundary is overflow, which debug builds check."),
    ],
    challenge=dict(
        function="seats_left",
        starter=code(r'''
            // JavaScript original:
            // function seatsLeft(capacity, booked, requested) {
            //   const left = capacity - booked - requested;
            //   return left >= 0 ? left : null;
            // }
            pub fn seats_left(capacity: u32, booked: u32, requested: u32) -> Option<u32> {
                todo!("implement the contract")
            }
        '''),
        cases=[
            ("visible", "solution::seats_left(100, 40, 10)", "Some(50)"),
            ("boundary", "solution::seats_left(10, 10, 0)", "Some(0)"),
            ("semantic", "solution::seats_left(10, 8, 3)", "None"),
            ("boundary", "solution::seats_left(10, u32::MAX, 1)", "None"),
            ("boundary", "solution::seats_left(u32::MAX, u32::MAX, 0)", "Some(0)"),
        ],
        solution=code(r'''
            pub fn seats_left(capacity: u32, booked: u32, requested: u32) -> Option<u32> {
                capacity.checked_sub(booked)?.checked_sub(requested)
            }
        '''),
        wrong=[
            ("plain subtraction, the JavaScript way", code(r'''
                pub fn seats_left(capacity: u32, booked: u32, requested: u32) -> Option<u32> {
                    Some(capacity - booked - requested)
                }
            ''')),
            ("adds the bookings first and overflows", code(r'''
                pub fn seats_left(capacity: u32, booked: u32, requested: u32) -> Option<u32> {
                    capacity.checked_sub(booked + requested)
                }
            ''')),
        ],
        js_lang="javascript",
        js_original=code(r'''
            function seatsLeft(capacity, booked, requested) {
              const left = capacity - booked - requested;
              return left >= 0 ? left : null;
            }
        '''),
        js_checks=[("seatsLeft(100, 40, 10)", 50), ("seatsLeft(10, 10, 0)", 0), ("seatsLeft(10, 8, 3)", None),
                   ("seatsLeft(10, 4294967295, 1)", None), ("seatsLeft(4294967295, 4294967295, 0)", 0)],
    ),
))

# ---------------------------------------------------------------- 4
LESSONS.append(dict(
    id="node-functions-to-fn",
    unit="node-values",
    title="JavaScript functions vs fn",
    concept="Typed parameters and tail expressions",
    minutes=10,
    kind="runnable",
    summary="A Rust function declares every parameter type and returns its final expression; there are no default parameters and no implicit coercions.",
    rule="Every parameter has a type, arguments must match it exactly, and a block's final expression without a semicolon is its value.",
    explanation=[
        "Arrow functions taught you expression bodies: `(x) => x * 2` returns without `return`. Rust applies that idea to every block. The last expression of a function body, without a trailing semicolon, is the return value. A semicolon turns it into a statement whose value is `()`, the unit type, so `fn double(x: i32) -> i32 { x * 2; }` is a type error. `return` still exists for early exits.",
        "Because `if` and `match` are expressions, there is no need for the ternary operator: `let base = if weight_kg <= 1 { 5 } else { 5 + (weight_kg - 1) * 2 };`. A block `{ ... }` is an expression too, which is how a function body produces its value.",
        "Parameters always have types, and the compiler never coerces arguments. JavaScript happily computed `shippingCost(\"3\")` as `9` through `\"3\" - 1`; Rust rejects a `&str` where a `u32` is expected, at the call site. There are no default or optional parameters and no overloading. Pass an explicit value, add a second function such as `discounted_default`, take an `Option<T>`, or group options in a struct that implements `Default`.",
        "The return type is part of the signature and is never inferred from the body. A function's contract stays readable without its body, and rustc can point at the exact semicolon that turned an `i32` into `()`.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        const double = (x) => x * 2;      // expression body: implicit return

        function shippingCost(weightKg, express = false) {
          const base = weightKg <= 1 ? 5 : 5 + (weightKg - 1) * 2;
          return express ? base * 2 : base;
        }

        console.log(double(21));
        console.log(shippingCost(3), shippingCost(3, true));
        console.log(shippingCost("3"));   // "3" - 1 is coerced: prints 9
    '''),
    from_stdout="42\n9 18\n9\n",
    from_caption="An implicit return in the arrow function, a default parameter, and a string silently coerced to a number.",
    example=code(r'''
        fn double(x: i32) -> i32 {
            x * 2
        }

        fn shipping_cost(weight_kg: u32, express: bool) -> u32 {
            let base = if weight_kg <= 1 { 5 } else { 5 + (weight_kg - 1) * 2 };
            if express { base * 2 } else { base }
        }

        fn main() {
            println!("{}", double(21));
            println!("{} {}", shipping_cost(3, false), shipping_cost(3, true));
        }
    '''),
    example_stdout="42\n9 18\n",
    example_caption="No `return` keywords: each body ends in an expression, and `if` replaces the ternary.",
    contrasts=[
        ("`(x) => x * 2` returns its expression; `{ x * 2; }` returns `undefined`.",
         "`{ x * 2 }` returns `x * 2`; `{ x * 2; }` evaluates to `()` and fails a `-> i32` signature."),
        ("`function f(express = false)` has a default.",
         "No default parameters: pass `false`, write a second function, or take an `Option<bool>`."),
        ("`shippingCost(\"3\")` coerces the string and returns `9`.",
         "A `&str` argument for a `u32` parameter is E0308 at the call."),
        ("`cond ? a : b`", "`if cond { a } else { b }`, an expression with a single type."),
    ],
    credits=["basics/functions", "basics/function-parameters", "basics/block-expressions"],
    practice=code(r'''
        fn double(x: i32) -> i32 {
            x * 2;
        }

        fn main() {
            println!("{}", double(21));
        }
    '''),
    practice_expect={"errors": ["E0308"], "messages": ["remove this semicolon"]},
    question="Why is `fn double(x: i32) -> i32 { x * 2; }` rejected?",
    answers=[
        "Rust needs `return` in every function",
        "`x * 2` must be wrapped in parentheses",
        "The semicolon makes the body evaluate to `()`, which is not `i32`",
    ],
    correct=2,
    feedback="With the semicolon, `x * 2` is a statement and the block's value is `()`. rustc reports E0308 and suggests removing the semicolon.",
    task="Port the JavaScript `discounted` shown at the top of solution.rs. Rust has no default parameters, so write `discounted(price_cents, percent)` and a separate `discounted_default(price_cents)` that applies 10 percent. A percent above 100 returns 0; otherwise subtract the discount, rounded down. In the Crabrix app, open the compiler lab and complete the supplied functions in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts both functions and the separate verification harness passes every case, including a percent above 100 and the default. Printing a success message alone does not complete this lab.",
    misconception="“Without `return`, a Rust function returns nothing, like a JavaScript function body without `return`.”",
    correction="A Rust block returns its final expression when it has no trailing semicolon. Only a semicolon, or an empty body, makes the value `()`.",
    trace=[
        ("Read the signature", "`shipping_cost(weight_kg: u32, express: bool) -> u32` names every input type and the output. Both arguments are required."),
        ("Find the tail values", "`let base = if ... { 5 } else { ... };` ends with a semicolon because it is a statement. The final `if express { base * 2 } else { base }` has none, so it is the return value."),
        ("Compare with evidence", "Run it: `42`, then `9 18`. Add `;` after the final `if` and rustc reports E0308, expected `u32`, found `()`."),
    ],
    transfer="Call `shipping_cost(\"3\", false)` and read where rustc places the error. Then rewrite `shipping_cost` with an early `return 5;` for light parcels and decide which version reads better.",
    connections=[("previous", "Number vs Rust integer types", "Explicit numeric types and overflow"),
                 ("next", "Truthiness vs bool, if and match", "No truthiness: conditions are bool")],
    recall=[
        dict(question="What type does `value` have, and why?",
             code=code(r'''
                 let value = {
                     let x = 3;
                     x + 1;
                 };
                 println!("{:?}", value);
             '''),
             answer="`()`. The semicolon after `x + 1` makes it a statement, so the block has no tail expression and evaluates to the unit value, and `{:?}` prints `()`. Remove the semicolon and `value` is the integer `4`.",
             expect={"stdout": "()\n"}),
        dict(question="Rust has no default parameters. What are three idiomatic replacements for `function connect(host, port = 5432)`?",
             answer="Require the argument and let callers pass `5432`; provide a second function such as `connect_default(host)`; or take `port: Option<u16>` and use `port.unwrap_or(5432)`. For many options, a config struct that implements `Default`, filled in with `..Default::default()`, scales better."),
    ],
    challenge=dict(
        function="discounted",
        starter=code(r'''
            // JavaScript original:
            // function discounted(priceCents, percent = 10) {
            //   if (percent > 100) return 0;
            //   const off = Math.floor(priceCents * percent / 100);
            //   return priceCents - off;
            // }
            pub fn discounted(price_cents: u64, percent: u64) -> u64 {
                todo!("implement the contract")
            }

            pub fn discounted_default(price_cents: u64) -> u64 {
                todo!("implement the contract")
            }
        '''),
        cases=[
            ("visible", "solution::discounted(1000, 10)", "900"),
            ("semantic", "solution::discounted(999, 10)", "900"),
            ("boundary", "solution::discounted(500, 150)", "0"),
            ("boundary", "solution::discounted(1000, 100)", "0"),
            ("semantic", "solution::discounted(0, 50)", "0"),
            ("visible", "solution::discounted_default(1000)", "900"),
        ],
        required=["pub fn discounted_default"],
        solution=code(r'''
            pub fn discounted(price_cents: u64, percent: u64) -> u64 {
                if percent > 100 {
                    return 0;
                }
                price_cents - price_cents * percent / 100
            }

            pub fn discounted_default(price_cents: u64) -> u64 {
                discounted(price_cents, 10)
            }
        '''),
        wrong=[
            ("early exit written as an if without else", code(r'''
                pub fn discounted(price_cents: u64, percent: u64) -> u64 {
                    if percent > 100 { 0 }
                    price_cents - price_cents * percent / 100
                }

                pub fn discounted_default(price_cents: u64) -> u64 {
                    discounted(price_cents, 10)
                }
            ''')),
            ("tail expression ends with a semicolon", code(r'''
                pub fn discounted(price_cents: u64, percent: u64) -> u64 {
                    if percent > 100 {
                        return 0;
                    }
                    price_cents - price_cents * percent / 100;
                }

                pub fn discounted_default(price_cents: u64) -> u64 {
                    discounted(price_cents, 10)
                }
            ''')),
            ("the default forgets the 10 percent", code(r'''
                pub fn discounted(price_cents: u64, percent: u64) -> u64 {
                    if percent > 100 {
                        return 0;
                    }
                    price_cents - price_cents * percent / 100
                }

                pub fn discounted_default(price_cents: u64) -> u64 {
                    discounted(price_cents, 0)
                }
            ''')),
        ],
        js_lang="javascript",
        js_original=code(r'''
            function discounted(priceCents, percent = 10) {
              if (percent > 100) return 0;
              const off = Math.floor(priceCents * percent / 100);
              return priceCents - off;
            }
        '''),
        js_checks=[("discounted(1000, 10)", 900), ("discounted(999, 10)", 900), ("discounted(500, 150)", 0),
                   ("discounted(1000, 100)", 0), ("discounted(0, 50)", 0), ("discounted(1000)", 900)],
    ),
))

# ---------------------------------------------------------------- 5
LESSONS.append(dict(
    id="node-truthiness-to-bool-and-match",
    unit="node-values",
    title="Truthiness vs bool, if and match",
    concept="No truthiness: conditions are bool",
    minutes=10,
    kind="runnable",
    summary="Rust has no truthy or falsy values: a condition must be a `bool`, and `if` and `match` are expressions whose branches share one type.",
    rule="`if` requires a `bool`, and every branch of an `if` or `match` expression must produce the same type.",
    explanation=[
        "`if (!count)` mixes several questions: is it `0`, `NaN`, `\"\"`, `null` or `undefined`? Rust refuses to guess. `if count` with an integer is E0308, expected `bool`, found integer, so you write the question you mean: `count == 0`, `text.is_empty()`, `value.is_none()`. There is no `==` versus `===` either. `==` compares two values of compatible types through `PartialEq` and never converts, so `0 == \"\"` does not compile.",
        "`if` is an expression, which replaces both the statement form and the ternary. `let urgent = if count > 0 && count < 5 { \"yes\" } else { \"no\" };` works because both branches are `&str`. If one branch yields a number and the other text, the expression has no single type and rustc rejects it. An `if` without `else` has type `()`, so it can only stand as a statement.",
        "`match` is the tool for several cases of one value. Patterns can be literals, ranges such as `1..=4`, or `_` for everything else, and the compiler checks that the arms cover every possible value. For a `u32`, the arms `0`, `1..=4` and `_` are exhaustive, so no input can fall through, unlike a `switch` without `default`.",
        "`&&` and `||` short-circuit as in JavaScript, but they accept and return only `bool`. There is no `a || b` default trick; that job belongs to `Option` methods such as `unwrap_or`, covered in the lesson on `null` and `undefined`.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        function stockLabel(count) {
          if (!count) return "sold out";   // 0, NaN, "" and undefined land here
          return count < 5 ? `only ${count} left` : "in stock";
        }

        console.log(stockLabel(0), "|", stockLabel(3), "|", stockLabel(12));
        console.log(stockLabel(NaN), "|", stockLabel("7"));
        console.log(Boolean("0"), Boolean([]), 0 == "", null == undefined);
    '''),
    from_stdout="sold out | only 3 left | in stock\nsold out | in stock\ntrue true true true\n",
    from_caption="Truthiness sends `0` and `NaN` to \"sold out\", and loose equality makes `0 == \"\"` true.",
    example=code(r'''
        fn stock_label(count: u32) -> String {
            match count {
                0 => String::from("sold out"),
                1..=4 => format!("only {count} left"),
                _ => String::from("in stock"),
            }
        }

        fn main() {
            let count = 3;
            let urgent = if count > 0 && count < 5 { "yes" } else { "no" };
            println!("{} | {} | {}", stock_label(0), stock_label(count), stock_label(12));
            println!("urgent: {urgent}");
        }
    '''),
    example_stdout="sold out | only 3 left | in stock\nurgent: yes\n",
    example_caption="`match` with a range covers every `u32`, and the `if` expression yields a `&str` from either branch.",
    contrasts=[
        ("`if (!count)` treats `0`, `NaN`, `\"\"`, `null` and `undefined` as false.",
         "`if count` is E0308; write `count == 0` or `text.is_empty()`."),
        ("`0 == \"\"` is `true`, which is why you use `===`.",
         "There is one `==` and it never converts: comparing an integer with a `&str` does not compile."),
        ("`a || b` returns one of its operands.",
         "`a || b` takes two `bool` values and returns a `bool`."),
        ("`switch` falls through and need not cover every case.",
         "`match` arms never fall through and must cover every value."),
    ],
    credits=["basics/booleans-comparisons", "basics/control-flow"],
    practice=code(r'''
        fn main() {
            let count = 3;
            if count {
                println!("in stock");
            }
        }
    '''),
    practice_expect={"errors": ["E0308"], "messages": ["expected `bool`, found integer"]},
    question="Why does `let label = if count > 0 { count } else { \"none\" };` not compile?",
    answers=[
        "`count > 0` is not a valid condition",
        "The branches produce different types: an integer and a `&str`",
        "`if` cannot appear on the right-hand side of `let`",
    ],
    correct=1,
    feedback="An `if` expression has one type. Return `count.to_string()` from the first branch and `String::from(\"none\")` from the second, or a number from both.",
    task="Port the JavaScript `fee` shown at the top of solution.rs. A zero amount is free, members pay no fee, and other amounts pay a fee of 2 when the amount is at least 100 and 5 below that. Write every condition as an explicit `bool`. In the Crabrix app, open the compiler lab and complete the supplied function in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including `0` and exactly `100`. Printing a success message alone does not complete this lab.",
    misconception="“`if count` works on numbers; Rust just treats `0` as false, like JavaScript.”",
    correction="Rust has no truthiness. A condition must have type `bool`, so you compare explicitly, for example `count != 0`.",
    trace=[
        ("Name each condition", "`stock_label` asks three exact questions with patterns: is it `0`, is it in `1..=4`, or is it anything else."),
        ("Check the types", "Every `match` arm yields a `String`. The `urgent` expression yields a `&str` from both branches, so each expression has one type."),
        ("Compare with evidence", "Run it: `sold out | only 3 left | in stock`, then `urgent: yes`. Delete the `_` arm and rustc reports E0004 for the values from 5 up to `u32::MAX`."),
    ],
    transfer="Add `fn describe(text: &str) -> &'static str` that returns `\"blank\"` for `\"\"` and for `\"   \"`, and `\"text\"` otherwise. In JavaScript `\"   \"` is truthy; decide which method expresses \"blank\" in Rust and why.",
    connections=[("previous", "JavaScript functions vs fn", "Typed parameters and tail expressions"),
                 ("next", "Classes and objects vs structs", "Data in structs, behaviour in impl blocks")],
    recall=[
        dict(question="What is the error, and what is the fix?",
             code=code(r'''
                 let name = String::new();
                 if name {
                     println!("named");
                 }
             '''),
             answer="E0308: the condition must be a `bool`, and a `String` is not one. Ask the exact question, such as `if !name.is_empty()`. Rust never converts a string, a number or an `Option` to a boolean.",
             expect={"errors": ["E0308"]}),
        dict(question="Which values of `n: u8` are not covered by this `match`?",
             code=code(r'''
                 let n: u8 = 7;
                 let size = match n {
                     0 => "zero",
                     1..=9 => "digit",
                     10..=99 => "two digits",
                 };
             '''),
             answer="`100..=255`. rustc rejects the `match` with E0004 and names that range. Add an arm for it or a `_` arm: a `match` must cover every value of the type.",
             expect={"errors": ["E0004"]}),
    ],
    challenge=dict(
        function="fee",
        starter=code(r'''
            // JavaScript original:
            // function fee(amount, isMember) {
            //   const rate = isMember ? 0 : amount >= 100 ? 2 : 5;
            //   return amount ? amount + rate : 0;
            // }
            pub fn fee(amount: u32, is_member: bool) -> u32 {
                todo!("implement the contract")
            }
        '''),
        cases=[
            ("visible", "solution::fee(50, false)", "55"),
            ("boundary", "solution::fee(0, false)", "0"),
            ("boundary", "solution::fee(100, false)", "102"),
            ("boundary", "solution::fee(99, false)", "104"),
            ("semantic", "solution::fee(50, true)", "50"),
            ("boundary", "solution::fee(0, true)", "0"),
        ],
        solution=code(r'''
            pub fn fee(amount: u32, is_member: bool) -> u32 {
                let rate = if is_member { 0 } else if amount >= 100 { 2 } else { 5 };
                if amount == 0 { 0 } else { amount + rate }
            }
        '''),
        wrong=[
            ("JavaScript truthiness kept in the condition", code(r'''
                pub fn fee(amount: u32, is_member: bool) -> u32 {
                    let rate = if is_member { 0 } else if amount >= 100 { 2 } else { 5 };
                    if amount { amount + rate } else { 0 }
                }
            ''')),
            ("forgets that a zero amount is free", code(r'''
                pub fn fee(amount: u32, is_member: bool) -> u32 {
                    let rate = if is_member { 0 } else if amount >= 100 { 2 } else { 5 };
                    amount + rate
                }
            ''')),
        ],
        js_lang="javascript",
        js_original=code(r'''
            function fee(amount, isMember) {
              const rate = isMember ? 0 : amount >= 100 ? 2 : 5;
              return amount ? amount + rate : 0;
            }
        '''),
        js_checks=[("fee(50, false)", 55), ("fee(0, false)", 0), ("fee(100, false)", 102),
                   ("fee(99, false)", 104), ("fee(50, true)", 50), ("fee(0, true)", 0)],
    ),
))
