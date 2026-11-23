"""Unit node-rust-at-a-glance: how Rust differs in general. Authored source for author.py."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


LESSONS = []

# ---------------------------------------------------------------- T1
LESSONS.append(dict(
    id="node-what-rust-is",
    unit="node-rust-at-a-glance",
    title="Node.js runtime vs compiled Rust",
    concept="Ahead-of-time compilation to a native executable",
    minutes=9,
    kind="planned",
    summary="Rust is compiled ahead of time to a native executable: rustc checks types, ownership and borrowing before anything runs, and there is no garbage collector or built-in event loop.",
    rule="Rust is a compiled, statically typed language without a garbage collector: rustc checks types, ownership and borrowing before the program runs, then produces a native executable.",
    explanation=[
        "`node app.js` starts a runtime. V8 parses your JavaScript, interprets it and compiles hot functions to machine code while the program runs, and the Node.js process supplies the event loop, the garbage collector and APIs such as `fs`. Every machine that runs the program needs Node.js too. Rust works ahead of time: `rustc`, usually driven by `cargo build`, reads the whole crate, checks it and writes a native executable for one target, such as macOS on Apple silicon or Linux on x86-64, or a WebAssembly module as in the Crabrix app. The result runs without Rust or Node.js installed.",
        "Checking happens before anything runs. rustc verifies types, ownership and borrowing in every function, including branches your tests never reach, and produces no executable while an error remains. The typo in the JavaScript `EUR` branch is a `TypeError` on the day that branch runs; the same typo in Rust is E0599 at build time. There is no separate `tsc` step to skip and no way to run the program anyway.",
        "Two things you take for granted are not built in. There is no garbage collector: each value has an owner and is freed at a known point, which the next lesson shows. There is no event loop either: async code needs a runtime library such as Tokio, chosen by the program. In exchange, a Rust executable has no JIT warm-up, and its memory use follows from the code rather than from collector heuristics.",
        "Static typing in Rust is mostly inferred. You annotate function signatures and struct fields; inside a function most `let` bindings need no annotation, and `let sum: u32 = prices.iter().sum();` needs one only because `sum` can produce several types. The types shape the compiled program: a `u32` occupies four bytes, and adding two of them compiles to an integer addition.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        // node app.js: V8 parses, interprets and JIT-compiles this while it runs.
        function total(prices, currency) {
          const sum = prices.reduce((acc, p) => acc + p, 0);
          if (currency === "EUR") {
            return sum.toFixd(2) + " EUR"; // typo: fails only when this branch runs
          }
          return String(sum);
        }

        console.log(total([3, 4], "USD"));
        console.log(process.release.name, typeof process.versions.v8);
        try {
          total([3, 4], "EUR");
        } catch (err) {
          console.log(err.constructor.name, err.message);
        }
    '''),
    from_stdout="7\nnode string\nTypeError sum.toFixd is not a function\n",
    from_caption="Node.js runs the file through V8, so the typo in the `EUR` branch surfaces as a `TypeError` only when that branch runs.",
    example=code(r'''
        // rustc main.rs (or cargo build) checks everything first, then writes an executable.
        fn total(prices: &[u32], currency: &str) -> String {
            let sum: u32 = prices.iter().sum();
            if currency == "EUR" {
                format!("{sum}.00 EUR")
            } else {
                sum.to_string()
            }
        }

        fn main() {
            println!("{}", total(&[3, 4], "USD"));
            println!("{}", total(&[3, 4], "EUR"));
            println!("{} {}", std::env::consts::OS, std::env::consts::ARCH);
        }
    '''),
    example_stdout="7\n7.00 EUR\nmacos aarch64\n",
    example_caption="rustc checked both branches before this ran. The last line names the compile target: `macos aarch64` on an Apple silicon Mac, `wasi wasm32` for the app's WebAssembly target.",
    contrasts=[
        ("`node app.js` needs Node.js on every machine that runs it.",
         "`cargo build` writes a native executable, or a WASM module, that runs without Rust or Node.js installed."),
        ("A typo in a branch is a `TypeError` only when that branch runs.",
         "rustc checks every branch first; the same typo is E0599, and no executable is built."),
        ("V8 interprets and JIT-compiles while the program runs.",
         "Compilation finishes before the program starts, so there is no JIT warm-up."),
        ("The garbage collector and the event loop come with the runtime.",
         "There is no garbage collector and no built-in event loop; async code uses a library such as Tokio."),
    ],
    credits=["basics/what-is-rust"],
    practice=code(r'''
        fn total(prices: &[u32], currency: &str) -> String {
            let sum: u32 = prices.iter().sum();
            if currency == "EUR" {
                return sum.to_strin() + " EUR";
            }
            sum.to_string()
        }

        fn main() {
            println!("{}", total(&[3, 4], "USD"));
        }
    '''),
    practice_expect={"errors": ["E0599"], "messages": ["no method named `to_strin` found"]},
    question="The `EUR` branch of the practice code has a typo, and your test only calls `total(&[3, 4], \"USD\")`. What happens?",
    answers=[
        "rustc refuses to build the program and reports E0599 for that branch, although it would never run",
        "The program runs and fails only if the `EUR` branch executes, like the `TypeError` in Node.js",
        "rustc prints a warning, and the executable skips the broken branch",
    ],
    correct=0,
    feedback="rustc checks every function and branch before it writes an executable. The typo is a compile error, E0599, whether or not a test reaches it.",
    task="Compile the practice code and read the error before running anything. Fix the typo, build again, and note that the program now runs although nothing ever calls the `EUR` branch.",
    success="You can explain why an error appears in a branch that never runs, and what file `rustc` or `cargo build` produces.",
    misconception="“Rust is like TypeScript: the types are checked, but the program still runs on a runtime such as Node.js.”",
    correction="rustc compiles the checked program ahead of time to machine code or WebAssembly. The executable contains no interpreter, JIT or garbage collector, and nothing like `node` is needed to run it.",
    trace=[
        ("Build before running", "`rustc main.rs` or `cargo build` reads the whole program. Nothing runs yet; `total` and `main` are checked completely."),
        ("Check every branch", "Both arms of the `if` are type-checked, although the `USD` call never takes the `EUR` arm. A typo in either would stop the build."),
        ("Compare with evidence", "Run it: `7`, `7.00 EUR`, then the target, `macos aarch64` on an Apple silicon Mac. Compile the practice code and read E0599 instead."),
    ],
    transfer="Build the example with `cargo build --release` and find the executable in `target/release/`. Copy it to another machine with the same OS and CPU architecture and no Rust installed, run it, and explain why a Linux server needs a binary built for Linux.",
    connections=[("next", "Garbage collection vs deterministic drop", "Deterministic drop at the end of scope")],
    recall=[
        dict(question="What does `cargo build` leave you with, and what must the machine that runs it have installed?",
             answer="A native executable in `target/debug/`, or `target/release/` with `--release`, built for one target such as Linux on x86-64. The machine needs a compatible operating system and CPU, not Rust, Cargo or Node.js. For a browser or a WASI host you build a WebAssembly module instead."),
        dict(question="Why is this rejected, even though nothing ever passes `true`?",
             code=code(r'''
                 fn label(verbose: bool) -> String {
                     if verbose {
                         return 42;
                     }
                     String::from("quiet")
                 }
             '''),
             answer="rustc type-checks every branch before it builds anything, whether or not the branch can run: E0308, expected `String`, found integer. There is no executable until the branch returns a `String`, for example `42.to_string()`.",
             expect={"errors": ["E0308"]}),
    ],
))

# ---------------------------------------------------------------- T2
LESSONS.append(dict(
    id="node-no-garbage-collector",
    unit="node-rust-at-a-glance",
    title="Garbage collection vs deterministic drop",
    concept="Deterministic drop at the end of scope",
    minutes=10,
    kind="planned",
    summary="V8's garbage collector frees objects whenever it decides; Rust drops each value at the end of its owner's scope, in an order you can read from the code.",
    rule="At scope end, remaining locals drop in reverse declaration order; struct fields drop in declaration order.",
    explanation=[
        "In Node.js, V8's garbage collector frees an object at some point after it becomes unreachable. The language leaves that point open: a `FinalizationRegistry` callback may run late, or not at all before the process exits, which is what the example shows. That is fine for memory, but it is why files, sockets and locks need an explicit `close()`, `try/finally` or `await handle.close()`; a forgotten handle stays open until the collector or the process exit gets to it.",
        "Rust has no collector. Every value has one owner, and when the owner goes out of scope the value is dropped right there: its `Drop` implementation runs, then its fields are dropped, then its memory is released. The order is defined. At the end of a scope the remaining locals drop in reverse declaration order, so the last one created is cleaned up first, and inside a struct the fields drop in declaration order. A value that was moved elsewhere is dropped by its new owner instead, exactly once.",
        "Because cleanup is tied to scope, one mechanism manages every resource. A `File` closes its descriptor in `Drop`, a `MutexGuard` unlocks its mutex, a `TcpStream` closes its socket and a `Vec` frees its buffer. There are no collection pauses and no finalizer threads; the cost of freeing appears at the closing brace where it happens.",
        "To release something earlier, end its scope or call `drop(value)`, the function `std::mem::drop`, which takes ownership and lets the value go. You never call the `drop` method yourself; rustc rejects that with E0040, because the destructor must run exactly once. Leaks are still possible, for example through `Rc` reference cycles or `std::mem::forget`, but they are explicit choices rather than an accident of the collector's timing.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        const registry = new FinalizationRegistry((name) => console.log(`collected ${name}`));

        function makeBuffers() {
          const first = { name: "first", data: new Array(1000).fill(0) };
          const second = { name: "second", data: new Array(1000).fill(0) };
          registry.register(first, "first");
          registry.register(second, "second");
          console.log("leaving makeBuffers");
        } // both objects are unreachable now, but nothing is freed yet

        makeBuffers();
        setTimeout(() => console.log("later: the collector decides when, if ever"), 10);
    '''),
    from_stdout="leaving makeBuffers\nlater: the collector decides when, if ever\n",
    from_caption="Both objects are unreachable once `makeBuffers` returns, but the collector decides when to free them, and here it never runs before the process exits.",
    example=code(r'''
        struct Noisy(&'static str);

        impl Drop for Noisy {
            fn drop(&mut self) {
                println!("drop {}", self.0);
            }
        }

        struct Pair {
            left: Noisy,
            right: Noisy,
        }

        fn make_buffers() {
            let _first = Noisy("first");
            let _second = Noisy("second");
            let _pair = Pair { left: Noisy("pair.left"), right: Noisy("pair.right") };
            println!("leaving make_buffers");
        }

        fn main() {
            make_buffers();
            let early = Noisy("early");
            drop(early);
            println!("end of main");
        }
    '''),
    example_stdout=("leaving make_buffers\ndrop pair.left\ndrop pair.right\ndrop second\ndrop first\n"
                    "drop early\nend of main\n"),
    example_caption="The last local drops first, a struct's fields drop in declaration order, and `drop(early)` releases a value before its scope ends.",
    contrasts=[
        ("V8 frees an unreachable object whenever its collector runs.",
         "A value is dropped at the end of its owner's scope, at a line you can point to."),
        ("A `FinalizationRegistry` callback may run late or never.",
         "`Drop::drop` runs exactly once, when the owner goes away or `drop(value)` is called."),
        ("Files and sockets need an explicit `close()` or `try/finally`.",
         "`File`, `TcpStream` and lock guards release their resource in `Drop`."),
        ("Collection pauses happen whenever the runtime decides.",
         "There is no collector and no collection pause; freeing happens where the scope ends."),
    ],
    credits=["ownership/drop-order"],
    practice=code(r'''
        struct Connection(&'static str);

        impl Drop for Connection {
            fn drop(&mut self) {
                println!("closing {}", self.0);
            }
        }

        fn main() {
            let conn = Connection("db");
            conn.drop();
            println!("done");
        }
    '''),
    practice_expect={"errors": ["E0040"]},
    question="In the example, which message prints right after `leaving make_buffers`?",
    answers=[
        "`drop first`, because `_first` was declared first",
        "Nothing yet: the memory is freed later, whenever the allocator decides",
        "`drop pair.left`: the last local drops first, and its fields drop in declaration order",
    ],
    correct=2,
    feedback="At the closing brace, `_pair` is the last declared local, so it drops first, `left` before `right`; then `_second` and `_first` follow.",
    task="Predict the order of all seven lines of the example before running it. Then move `let _second` into an inner block of its own and predict again.",
    success="Your predicted order matches the output, including the two `pair` fields, and you can say where each value's memory is released.",
    misconception="“Rust frees memory at some later point, like a garbage collector, only faster.”",
    correction="There is no later point. A value is dropped exactly when its owner's scope ends, or when it is passed to `drop`, and the order follows the declarations.",
    trace=[
        ("List the owners", "`make_buffers` owns `_first`, `_second` and `_pair`, and `_pair` owns two `Noisy` fields. `main` owns `early`."),
        ("Close the scope", "At the closing brace of `make_buffers`, `_pair` drops first, `pair.left` and then `pair.right`; then `_second`, then `_first`."),
        ("Compare with evidence", "Run it: `leaving make_buffers`, the four drops in that order, `drop early`, then `end of main`. Nothing is left for later."),
    ],
    transfer="Return `_second` from `make_buffers` and bind it in `main`. Predict where `drop second` moves in the output, and say which owner drops it now.",
    connections=[("previous", "Node.js runtime vs compiled Rust", "Ahead-of-time compilation to a native executable"),
                 ("next", "TypeScript types vs Rust types", "Types the compiler enforces, and its diagnostics")],
    recall=[
        dict(question="What does this print, and in what order?",
             code=code(r'''
                 struct Tag(&'static str);
                 impl Drop for Tag {
                     fn drop(&mut self) { println!("drop {}", self.0); }
                 }
                 fn main() {
                     let a = Tag("a");
                     let b = Tag("b");
                     let moved = a;
                     println!("body");
                 }
             '''),
             answer="`body`, then `drop a`, then `drop b`. Moving `a` into `moved` hands the drop to `moved`, the last declared local, so it drops first, and `b` follows. The original binding `a` runs no destructor of its own.",
             expect={"stdout": "body\ndrop a\ndrop b\n"}),
        dict(question="Why does rustc reject `conn.drop()`, and what do you write instead?",
             answer="Calling the destructor method directly would let it run twice, once now and again at the end of the scope, so rustc rejects it with E0040. Write `drop(conn)`: the function takes ownership, the value is dropped inside it, and the binding cannot be used afterwards."),
    ],
))

# ---------------------------------------------------------------- T3
LESSONS.append(dict(
    id="node-types-are-checked-not-erased",
    unit="node-rust-at-a-glance",
    title="TypeScript types vs Rust types",
    concept="Types the compiler enforces, and its diagnostics",
    minutes=11,
    kind="planned",
    summary="TypeScript types are erased and can be bypassed with `any` or `as`; Rust types are enforced by rustc, which builds nothing until its diagnostics are fixed.",
    rule="rustc refuses to build a program with a type error: read each diagnostic's code, span and labels, and repair the first causal error before chasing its downstream messages.",
    explanation=[
        "TypeScript checks your code and then erases the types: the JavaScript that runs has no idea a `User` exists. `JSON.parse(raw) as User` is a promise to the compiler that nothing verifies, `any` switches checking off, and a wrong assertion raises no error. In the example, `user.id + 1` type-checks as numeric addition and produces the string `\"421\"` at runtime.",
        "Rust has no `any` and no unchecked assertion between unrelated types. A value of type `u32` is a `u32` in the compiled program; text from outside becomes one only through a step that can fail and says so, such as `\"42\".parse::<u32>()`, which returns a `Result`. Serde's `serde_json::from_str::<User>` works the same way: a JSON string where the struct expects a number is an `Err`, not a quietly wrong object. The escape hatches that do exist, `as` between numeric types and `unsafe` code, are narrow and visible.",
        "Because rustc refuses to build a program with a type error, reading its diagnostics is a daily skill. Each error has a code such as `E0308`, a primary span marked with `^^^` under the offending expression, labels such as `expected u32, found &str`, and often a `help:` line with a suggestion. `rustc --explain E0308` prints a longer explanation with examples. Treat a suggestion as a hint rather than an order: decide first what the program should mean.",
        "Read the errors from the top and repair the first causal one. In the practice code, `id` is text, so both `id + 1` and `User { id }` fail; the root cause is the missing parse, and once `id` is a `u32` both messages disappear. Patching each later message with a cast or an annotation hides the real mistake and can create new errors further down.",
    ],
    from_lang="typescript",
    from_label="TypeScript",
    from_code=code(r'''
        interface User {
          id: number;
          name: string;
        }

        const raw = '{"id": "42", "name": null}';
        const user = JSON.parse(raw) as User; // the assertion is never checked
        console.log(typeof user.id, user.id + 1);

        const anything: any = user.name;
        try {
          console.log(anything.toUpperCase()); // compiles, fails at runtime
        } catch (err) {
          console.log((err as Error).message);
        }
    '''),
    from_stdout="string 421\nCannot read properties of null (reading 'toUpperCase')\n",
    from_caption="The assertion and `any` satisfy `tsc`, and then the runtime adds a string to a number and calls a method on `null`.",
    example=code(r'''
        #[derive(Debug)]
        struct User {
            id: u32,
            name: String,
        }

        fn parse_user(id: &str, name: Option<&str>) -> Result<User, String> {
            let id: u32 = id.parse().map_err(|e| format!("id {id:?}: {e}"))?;
            let name = name.ok_or("name is missing")?.to_string();
            Ok(User { id, name })
        }

        fn main() {
            println!("{:?}", parse_user("42", Some("ana")));
            println!("{:?}", parse_user("4x2", Some("ana")));
            println!("{:?}", parse_user("42", None));
        }
    '''),
    example_stdout=("Ok(User { id: 42, name: \"ana\" })\nErr(\"id \\\"4x2\\\": invalid digit found in string\")\n"
                    "Err(\"name is missing\")\n"),
    example_caption="Outside text becomes a `User` only through parsing, and each failure says what was wrong.",
    contrasts=[
        ("`JSON.parse(raw) as User` is never checked at runtime.",
         "Text becomes a `User` only through parsing that returns a `Result`."),
        ("`any` turns type checking off for a value.",
         "There is no `any`: every value has one concrete type that the compiler knows."),
        ("Types are erased before the JavaScript runs.",
         "Types shape the compiled code: a `u32` is four bytes, and `+` on it is integer addition."),
        ("A `tsc` error can be ignored, and the emitted JavaScript still runs.",
         "rustc builds nothing until every error is fixed."),
    ],
    credits=["basics/compiler-feedback"],
    practice=code(r'''
        struct User {
            id: u32,
        }

        fn main() {
            let id = "42";
            let next = id + 1;
            let user = User { id };
            println!("{} {}", user.id, next);
        }
    '''),
    practice_expect={"errors": ["E0369", "E0308"], "messages": ["expected `u32`, found `&str`"]},
    question="For the practice code, rustc reports E0369 at `id + 1` and E0308 at `User { id }`. What do you fix first?",
    answers=[
        "The `User` struct: change its `id` field to `&str`",
        "The binding `id`: both errors start where text is used as a number, so parse it once with `\"42\".parse::<u32>()`",
        "Add `as u32` at both error sites",
    ],
    correct=1,
    feedback="Both diagnostics trace back to `id` being a `&str`. Parsing it into a `u32` removes the root cause, and both messages go away; `as` cannot convert text at all (E0606).",
    task="Compile the practice code and read both errors: the code, the primary span and the labels. Fix only the root cause, compile again and confirm that both messages are gone. Then run `rustc --explain E0369`.",
    success="You fixed both errors with one change, and you can point to the span and label that revealed the root cause.",
    misconception="“`as` in Rust works like a TypeScript assertion: it tells the compiler to treat a value as another type.”",
    correction="Rust's `as` performs a real conversion between compatible primitive types and is rejected for anything else, such as `&str` to `u32` (E0606). Converting outside data is a fallible operation such as `parse`.",
    trace=[
        ("Read the types", "`User.id` is a `u32`, and `parse_user` receives text. The only way from one to the other is `id.parse()`, which returns a `Result`."),
        ("Follow the failures", "`\"4x2\"` fails in `parse`, and the error says why; a missing name fails in `ok_or`. Neither path can produce a half-valid `User`."),
        ("Compare with evidence", "Run it: `Ok(User { id: 42, name: \"ana\" })`, then an `Err` naming the invalid digit in `\"4x2\"`, then `Err(\"name is missing\")`."),
    ],
    transfer="Call `parse_user(\"-1\", Some(\"ana\"))` and `parse_user(\"4294967296\", Some(\"ana\"))`, predict both error messages and check them. Then name the JavaScript expression that would have accepted each value without complaint.",
    connections=[("previous", "Garbage collection vs deterministic drop", "Deterministic drop at the end of scope"),
                 ("next", "console.log vs println!", "Compile-time checked formatting")],
    recall=[
        dict(question="Why is this rejected, and what is the fix?",
             code=code(r'''
                 let raw = "42";
                 let id = raw as u32;
             '''),
             answer="`as` converts only between compatible primitive types; it is not an unchecked assertion like TypeScript's `as`. Casting a `&str` to a `u32` is E0606. Parse instead, with `let id: u32 = raw.parse()?;` or a `match` on the `Result`.",
             expect={"errors": ["E0606"]}),
        dict(question="rustc prints `error[E0308]: mismatched types`, a `^^^` span and the label `expected u32, found &str`. What does each part tell you, and where do you find more?",
             answer="`E0308` names the rule that was broken, the span marks the exact expression, and the label compares the type the context requires with the type the expression has. `rustc --explain E0308` prints a longer explanation with examples. Start with the first such error, because later ones are often consequences of it."),
    ],
))
