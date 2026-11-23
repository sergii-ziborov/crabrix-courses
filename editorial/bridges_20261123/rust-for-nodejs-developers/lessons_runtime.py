"""Unit node-runtime: errors, packages and async. Authored source for author.py."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


LESSONS = []

# ---------------------------------------------------------------- 15
LESSONS.append(dict(
    id="node-try-catch-to-result",
    unit="node-runtime",
    title="try/catch vs Result",
    concept="Errors as Result values",
    minutes=12,
    kind="runnable",
    summary="`throw` and `try/catch` become `Result<T, E>`: failure is part of the return type, `?` propagates it, and panics are reserved for bugs.",
    rule="Return `Result` for a failure the caller can act on, propagate it with `?`, and keep panics such as `unwrap` for bugs and broken invariants.",
    explanation=[
        "In JavaScript any function may throw anything, and nothing in its signature says so. A caller learns that `parsePort` throws by reading its code or by watching it crash. Rust puts failure in the type: `fn parse_port(text: &str) -> Result<u16, PortError>` returns either `Ok(port)` or `Err(reason)`, and the caller cannot reach the `u16` without deciding what to do about the error.",
        "The error type is yours to design. An enum such as `PortError { NotANumber(ParseIntError), OutOfRange(u32) }` lets a caller tell the cases apart with `match` instead of comparing message strings, and it can wrap the lower-level error as its cause. `map_err` converts one error type into another, and the `?` operator returns the `Err` early, like an exception propagating, but visibly at every call site and only from a function that itself returns a compatible `Result`.",
        "Panics are not exceptions. `unwrap()`, `expect()`, indexing out of bounds and integer overflow in a debug build panic: the thread unwinds, or the process aborts if the build sets `panic = \"abort\"`. Use them for bugs, where continuing would be wrong, not for invalid user input. A `Result` is for situations the caller can reasonably handle: bad text, a missing file, a refused connection.",
        "Parsing stops being lenient as well. `Number(\"\")` is `0` and `Number(\"0x50\")` is `80`, while `\"\".parse::<u32>()` is an `Err` of kind `Empty` and `\"0x50\"` one of kind `InvalidDigit`. One surprise runs the other way: integer `parse` accepts a leading `+`, so validate the exact format first when your contract forbids a sign.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        function parsePort(text) {
          const n = Number(text);
          if (!Number.isInteger(n) || n < 1 || n > 65535) {
            throw new Error(`invalid port: ${JSON.stringify(text)}`);
          }
          return n;
        }

        for (const input of ["8080", "", "0x50", "70000"]) {
          try {
            console.log(input, "->", parsePort(input));
          } catch (err) {
            console.log(input, "->", err.message);
          }
        }
    '''),
    from_stdout="8080 -> 8080\n -> invalid port: \"\"\n0x50 -> 80\n70000 -> invalid port: \"70000\"\n",
    from_caption="`Number` reads `\"\"` as `0` and `\"0x50\"` as `80`, and the only signal of failure is a thrown `Error`.",
    example=code(r'''
        use std::num::ParseIntError;

        #[derive(Debug)]
        enum PortError {
            NotANumber(ParseIntError),
            OutOfRange(u32),
        }

        fn parse_port(text: &str) -> Result<u16, PortError> {
            let n: u32 = text.parse().map_err(PortError::NotANumber)?;
            match u16::try_from(n) {
                Ok(port) if port != 0 => Ok(port),
                _ => Err(PortError::OutOfRange(n)),
            }
        }

        fn main() {
            for input in ["8080", "", "0x50", "70000"] {
                match parse_port(input) {
                    Ok(port) => println!("{input} -> {port}"),
                    Err(err) => println!("{input} -> {err:?}"),
                }
            }
        }
    '''),
    example_stdout="8080 -> 8080\n -> NotANumber(ParseIntError { kind: Empty })\n0x50 -> NotANumber(ParseIntError { kind: InvalidDigit })\n70000 -> OutOfRange(70000)\n",
    example_caption="`?` returns the wrapped parse error early, the range check produces its own variant, and `main` matches both.",
    contrasts=[
        ("Any function may `throw`, and its signature does not say so.",
         "`-> Result<u16, PortError>` declares the failure, and callers must handle it."),
        ("`catch (err)` receives anything, often just a message.",
         "A `match` on an error enum tells the cases apart by type."),
        ("An uncaught exception bubbles up invisibly.",
         "`?` propagates an `Err` explicitly, at each call site."),
        ("`Number(\"\")` is `0`, and `Number(\"0x50\")` is `80`.",
         "`\"\".parse::<u32>()` fails with kind `Empty`, and `\"0x50\"` with `InvalidDigit`."),
    ],
    credits=["basics/recoverable-errors", "projects/errors"],
    practice=code(r'''
        fn main() {
            let input = "70000";
            let port: u16 = input.parse().unwrap();
            println!("{port}");
        }
    '''),
    practice_expect={"panic": "called `Result::unwrap()` on an `Err` value: ParseIntError { kind: PosOverflow }"},
    question="In the practice code, what does `unwrap()` do when `parse` returns `Err`?",
    answers=[
        "It panics: the thread unwinds, or the process aborts if panics are configured to abort",
        "It returns the `Err` to the caller automatically, like an uncaught `throw` bubbling up",
        "It returns `0`, as `Number` does for bad input",
    ],
    correct=0,
    feedback="`unwrap` is a deliberate crash on `Err`. Handing the error back to the caller is what `?` does.",
    task="Port the JavaScript `parseDuration` shown at the top of solution.rs. Accept ASCII digits followed by `s`, `m` or `h`. Return `DurationError::BadFormat` for anything else, including a missing number or a sign, and `DurationError::TooLong` above 86,400 seconds, even when the number does not fit an integer type. In the Crabrix app, open the compiler lab and complete the supplied function in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including `24h`, `+5s` and a number too large for `u32`. Printing a success message alone does not complete this lab.",
    misconception="“`unwrap()` is like letting the exception propagate to a caller's `try/catch`.”",
    correction="`unwrap()` panics. To let the caller handle the error, return a `Result` and use `?`, which hands the `Err` back.",
    trace=[
        ("Read the signature", "`parse_port` returns `Result<u16, PortError>`. Both kinds of failure are variants a caller can `match` on."),
        ("Follow each input", "`\"\"` and `\"0x50\"` fail in `parse`, and `?` returns them wrapped in `NotANumber`. `\"70000\"` parses as a `u32`, but `u16::try_from` fails, giving `OutOfRange(70000)`."),
        ("Compare with evidence", "Run it: `8080 -> 8080`, then `NotANumber` with kinds `Empty` and `InvalidDigit`, then `OutOfRange(70000)`. JavaScript accepted `0x50` as port 80."),
    ],
    transfer="Implement `std::fmt::Display` for `PortError` so that `main` can print `invalid port: out of range (70000)`. Then write `fn parse_address(text: &str) -> Result<(String, u16), PortError>` that splits `host:port` and uses `?` on `parse_port`.",
    connections=[("previous", "TypeScript interfaces vs traits", "Nominal traits instead of structural interfaces"),
                 ("next", "npm and package.json vs Cargo", "package.json and npm mapped to Cargo")],
    recall=[
        dict(question="Why does `?` not compile here, and how do you fix it?",
             code=code(r'''
                 fn port() -> u16 {
                     let n: u16 = "8080".parse()?;
                     n
                 }
             '''),
             answer="`?` hands the error back to the caller, so the function itself must return a compatible `Result` or `Option`: E0277. Change the signature to `fn port() -> Result<u16, std::num::ParseIntError>` and return `Ok(n)`.",
             expect={"errors": ["E0277"]}),
        dict(question="When is `expect(\"...\")` acceptable instead of returning a `Result`?",
             answer="When an `Err` would mean a bug in your own program, such as parsing a constant literal or a value an earlier check guaranteed. The message documents the broken invariant. For anything that depends on input, files or the network, return a `Result` so that the caller can respond."),
    ],
    challenge=dict(
        function="parse_duration",
        starter=code(r'''
            // JavaScript original:
            // function parseDuration(text) {            // "90s", "15m", "2h"
            //   const match = /^(\d+)([smh])$/.exec(text);
            //   if (!match) throw new Error("bad format");
            //   const seconds = Number(match[1]) * { s: 1, m: 60, h: 3600 }[match[2]];
            //   if (seconds > 86400) throw new Error("too long");
            //   return seconds;
            // }
            #[derive(Debug, PartialEq)]
            pub enum DurationError {
                BadFormat,
                TooLong,
            }

            pub fn parse_duration(text: &str) -> Result<u32, DurationError> {
                todo!("implement the contract")
            }
        '''),
        harness=code(r'''
            mod solution;

            use solution::DurationError::{BadFormat, TooLong};

            fn main() {
                assert_eq!(solution::parse_duration("90s"), Ok(90), "case 1");
                assert_eq!(solution::parse_duration("15m"), Ok(900), "case 2");
                assert_eq!(solution::parse_duration("24h"), Ok(86_400), "case 3");
                assert_eq!(solution::parse_duration("25h"), Err(TooLong), "case 4");
                assert_eq!(solution::parse_duration("h"), Err(BadFormat), "case 5");
                assert_eq!(solution::parse_duration(""), Err(BadFormat), "case 6");
                assert_eq!(solution::parse_duration("1.5h"), Err(BadFormat), "case 7");
                assert_eq!(solution::parse_duration("+5s"), Err(BadFormat), "case 8");
                assert_eq!(solution::parse_duration("5d"), Err(BadFormat), "case 9");
                assert_eq!(solution::parse_duration("99999999999s"), Err(TooLong), "case 10");
                assert_eq!(solution::parse_duration("5é"), Err(BadFormat), "case 11");

                println!("PASS node-try-catch-to-result");
            }
        '''),
        cases=[
            ("visible", "solution::parse_duration(\"90s\")", "Ok(90)"),
            ("semantic", "solution::parse_duration(\"15m\")", "Ok(900)"),
            ("boundary", "solution::parse_duration(\"24h\")", "Ok(86400)"),
            ("boundary", "solution::parse_duration(\"25h\")", "Err(TooLong)"),
            ("boundary", "solution::parse_duration(\"h\") and (\"\")", "Err(BadFormat)"),
            ("semantic", "solution::parse_duration(\"1.5h\"), (\"+5s\"), (\"5d\"), (\"5é\")", "Err(BadFormat)"),
            ("boundary", "solution::parse_duration(\"99999999999s\")", "Err(TooLong)"),
        ],
        solution=code(r'''
            #[derive(Debug, PartialEq)]
            pub enum DurationError {
                BadFormat,
                TooLong,
            }

            pub fn parse_duration(text: &str) -> Result<u32, DurationError> {
                let (digits, unit) = match text.char_indices().last() {
                    Some((index, unit)) => (&text[..index], unit),
                    None => return Err(DurationError::BadFormat),
                };
                let factor: u64 = match unit {
                    's' => 1,
                    'm' => 60,
                    'h' => 3600,
                    _ => return Err(DurationError::BadFormat),
                };
                if digits.is_empty() || !digits.bytes().all(|b| b.is_ascii_digit()) {
                    return Err(DurationError::BadFormat);
                }
                // Only ASCII digits remain, so a failed parse means the number is too large.
                let n: u64 = digits.parse().map_err(|_| DurationError::TooLong)?;
                let seconds = n.checked_mul(factor).ok_or(DurationError::TooLong)?;
                if seconds > 86_400 {
                    return Err(DurationError::TooLong);
                }
                u32::try_from(seconds).map_err(|_| DurationError::TooLong)
            }
        '''),
        wrong=[
            ("lets parse decide: accepts +5 and calls a huge number BadFormat", code(r'''
                #[derive(Debug, PartialEq)]
                pub enum DurationError {
                    BadFormat,
                    TooLong,
                }

                pub fn parse_duration(text: &str) -> Result<u32, DurationError> {
                    let (digits, unit) = match text.char_indices().last() {
                        Some((index, unit)) => (&text[..index], unit),
                        None => return Err(DurationError::BadFormat),
                    };
                    let factor = match unit {
                        's' => 1,
                        'm' => 60,
                        'h' => 3600,
                        _ => return Err(DurationError::BadFormat),
                    };
                    let n: u32 = digits.parse().map_err(|_| DurationError::BadFormat)?;
                    let seconds = n.checked_mul(factor).ok_or(DurationError::TooLong)?;
                    if seconds > 86_400 {
                        return Err(DurationError::TooLong);
                    }
                    Ok(seconds)
                }
            ''')),
            ("splits off the unit by byte and panics on non-ASCII input", code(r'''
                #[derive(Debug, PartialEq)]
                pub enum DurationError {
                    BadFormat,
                    TooLong,
                }

                pub fn parse_duration(text: &str) -> Result<u32, DurationError> {
                    if text.is_empty() {
                        return Err(DurationError::BadFormat);
                    }
                    let (digits, unit) = text.split_at(text.len() - 1);
                    let factor: u64 = match unit {
                        "s" => 1,
                        "m" => 60,
                        "h" => 3600,
                        _ => return Err(DurationError::BadFormat),
                    };
                    if digits.is_empty() || !digits.bytes().all(|b| b.is_ascii_digit()) {
                        return Err(DurationError::BadFormat);
                    }
                    let n: u64 = digits.parse().map_err(|_| DurationError::TooLong)?;
                    let seconds = n.checked_mul(factor).ok_or(DurationError::TooLong)?;
                    if seconds > 86_400 {
                        return Err(DurationError::TooLong);
                    }
                    Ok(seconds as u32)
                }
            ''')),
            ("panics instead of returning an error", code(r'''
                #[derive(Debug, PartialEq)]
                pub enum DurationError {
                    BadFormat,
                    TooLong,
                }

                pub fn parse_duration(text: &str) -> Result<u32, DurationError> {
                    let (digits, unit) = text.split_at(text.len() - 1);
                    let factor = match unit {
                        "s" => 1,
                        "m" => 60,
                        _ => 3600,
                    };
                    let n: u32 = digits.parse().unwrap();
                    Ok(n * factor)
                }
            ''')),
        ],
        js_lang="javascript",
        js_original=code(r'''
            function parseDuration(text) {
              const match = /^(\d+)([smh])$/.exec(text);
              if (!match) throw new Error("bad format");
              const seconds = Number(match[1]) * { s: 1, m: 60, h: 3600 }[match[2]];
              if (seconds > 86400) throw new Error("too long");
              return seconds;
            }
            function attempt(text) {
              try { return parseDuration(text); } catch (err) { return err.message; }
            }
        '''),
        js_checks=[("attempt(\"90s\")", 90), ("attempt(\"15m\")", 900), ("attempt(\"24h\")", 86400),
                   ("attempt(\"25h\")", "too long"), ("attempt(\"h\")", "bad format"), ("attempt(\"\")", "bad format"),
                   ("attempt(\"1.5h\")", "bad format"), ("attempt(\"+5s\")", "bad format"),
                   ("attempt(\"5d\")", "bad format"), ("attempt(\"99999999999s\")", "too long"),
                   ("attempt(\"5é\")", "bad format")],
    ),
))

# ---------------------------------------------------------------- 16
PACKAGE_RUNNER = code(r'''
    // Reads the lesson's package.json and reports what npm's own semver library accepts.
    const fs = require("fs");
    const semver = require("semver");
    const pkg = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
    for (const [name, range] of Object.entries({ ...pkg.dependencies, ...pkg.devDependencies })) {
      console.log(`${name} "${range}" -> ${new semver.Range(range).range}`);
    }
    console.log(`left-pad 1.3.1 allowed: ${semver.satisfies("1.3.1", pkg.dependencies["left-pad"])}`);
    console.log(`express 4.21.2 allowed: ${semver.satisfies("4.21.2", pkg.dependencies.express)}`);
    console.log(`^0.4.1 allows 0.5.0: ${semver.satisfies("0.5.0", "^0.4.1")}`);
    console.log(`targets: main=${pkg.main} bin=${pkg.bin.invoice} test="${pkg.scripts.test}"`);
''') + "\n"

LESSONS.append(dict(
    id="node-npm-to-cargo",
    unit="node-runtime",
    title="npm and package.json vs Cargo",
    concept="package.json and npm mapped to Cargo",
    minutes=10,
    kind="planned",
    summary="`package.json` becomes `Cargo.toml`, `package-lock.json` becomes `Cargo.lock`, and npm scripts become built-in Cargo commands, but a bare version number means something different.",
    rule="In `Cargo.toml` a bare version such as `\"1.3.0\"` is a caret requirement, `>=1.3.0, <2.0.0`; pin exactly with `\"=1.3.0\"`, and let `Cargo.lock` record what was resolved.",
    explanation=[
        "The files map closely. `Cargo.toml` is the manifest: `[package]` holds the name, version and edition, `[dependencies]` and `[dev-dependencies]` match their npm counterparts, and `[build-dependencies]` serve a `build.rs` script. `Cargo.lock` records the exact resolved versions, like `package-lock.json`; commit it for applications. Downloaded crate sources are cached once per user under `~/.cargo/registry`, and build output goes to `target/`, so there is no `node_modules` directory.",
        "The version trap: in `package.json`, `\"left-pad\": \"1.3.0\"` pins exactly that version, and only `\"^1.3.0\"` allows updates. In `Cargo.toml`, `left-pad = \"1.3.0\"` already means `^1.3.0`, at least 1.3.0 and below 2.0.0. For `0.x` versions the caret is narrower in both tools, so `\"0.4.1\"` allows `>=0.4.1, <0.5.0`. To pin exactly, write `\"=1.3.0\"`; most projects rely on the lockfile instead.",
        "There is no `scripts` section and no `main` or `bin` field. Cargo finds targets by path: `src/main.rs` is the default binary, `src/lib.rs` the library, and each file in `src/bin/` an extra binary. `cargo build`, `cargo run`, `cargo test`, `cargo check` and `cargo fmt` are built in; project-specific tasks usually become a small binary or an `xtask` crate.",
        "Dependencies must be declared to be visible. Node resolves `require(\"serde\")` by walking up the directory tree to any `node_modules`, so an undeclared package can work by accident. Cargo passes only the declared crates to rustc, which is why the practice code fails with E0432 instead of finding a crate that happens to be on disk. Optional functionality is chosen with features, as in `serde = { version = \"1\", features = [\"derive\"] }`.",
    ],
    from_lang="javascript",
    from_label="Node.js (package.json)",
    from_code=code(r'''
        {
          "name": "invoice",
          "version": "0.1.0",
          "main": "src/index.js",
          "bin": { "invoice": "bin/invoice.js" },
          "scripts": { "test": "node --test", "start": "node bin/invoice.js" },
          "dependencies": {
            "express": "^4.19.2",
            "left-pad": "1.3.0"
          },
          "devDependencies": { "prettier": "^3.3.0" }
        }
    '''),
    from_runner=PACKAGE_RUNNER,
    from_stdout=("express \"^4.19.2\" -> >=4.19.2 <5.0.0-0\nleft-pad \"1.3.0\" -> 1.3.0\n"
                 "prettier \"^3.3.0\" -> >=3.3.0 <4.0.0-0\nleft-pad 1.3.1 allowed: false\n"
                 "express 4.21.2 allowed: true\n^0.4.1 allows 0.5.0: false\n"
                 "targets: main=src/index.js bin=bin/invoice.js test=\"node --test\"\n"),
    from_caption="A typical manifest: the bare `\"1.3.0\"` pins exactly, `^` allows compatible updates, and scripts name the commands.",
    example=code(r'''
        // Cargo.toml
        // [package]
        // name = "invoice"
        // version = "0.1.0"
        // edition = "2024"
        //
        // [dependencies]
        // serde = "1.0.200"   # means ^1.0.200, like npm "^1.0.200"
        // itoa = "=1.0.11"    # an exact pin, like npm's bare "1.0.11"
        //
        // [dev-dependencies]
        // pretty_assertions = "1"
        //
        // src/main.rs is the default binary: `cargo run` builds and runs it.
        fn main() {
            let version = option_env!("CARGO_PKG_VERSION").unwrap_or("outside Cargo");
            println!("invoice {version}");
        }
    '''),
    example_stdout="invoice outside Cargo\n",
    example_caption="The manifest lives in `Cargo.toml`, `src/main.rs` is the binary target, and Cargo sets `CARGO_PKG_VERSION` when it builds.",
    contrasts=[
        ("`\"left-pad\": \"1.3.0\"` pins exactly 1.3.0.",
         "`left-pad = \"1.3.0\"` means `^1.3.0`; pin exactly with `\"=1.3.0\"`."),
        ("`package-lock.json` records the resolved versions.",
         "`Cargo.lock` does the same, and Cargo keeps it while it still satisfies `Cargo.toml`."),
        ("`main`, `bin` and `scripts` are declared in `package.json`.",
         "Targets come from paths such as `src/main.rs` and `src/lib.rs`; the commands are built in."),
        ("`require` can find an undeclared package in a parent `node_modules`.",
         "rustc sees only declared dependencies; an undeclared crate is an unresolved import, E0432."),
    ],
    credits=["projects/dependencies"],
    practice=code(r'''
        use serde::Serialize;

        #[derive(Serialize)]
        struct Invoice {
            total_cents: u64,
        }

        fn main() {
            let invoice = Invoice { total_cents: 1200 };
            println!("{}", invoice.total_cents);
        }
    '''),
    practice_expect={"errors": ["E0432"]},
    question="In `package.json`, a bare `\"1.3.0\"` pins exactly that version. What does `left-pad = \"1.3.0\"` mean in `Cargo.toml`?",
    answers=[
        "Exactly 1.3.0, as in npm",
        "Any version at all; only the lockfile decides",
        "Any SemVer-compatible version: at least 1.3.0 and below 2.0.0",
    ],
    correct=2,
    feedback="Cargo's default requirement is the caret, so `\"1.3.0\"` means `^1.3.0`. Write `\"=1.3.0\"` for an exact pin.",
    task="Write the `Cargo.toml` for an equivalent Rust project: one dependency with a compatible range, one pinned exactly, one dev-dependency, and the paths that replace `main`, `bin` and `scripts.test`. Then check each version requirement against the rules above.",
    success="Your manifest uses `=` only where an exact pin is intended, and you can name the default binary and library paths without looking them up.",
    misconception="“`serde = \"1.0.200\"` pins serde exactly, like a bare version in `package.json`.”",
    correction="A bare version in `Cargo.toml` is a caret requirement. It accepts any later 1.x release, and `Cargo.lock` records the one Cargo actually chose.",
    trace=[
        ("Map the manifest", "`[dependencies]` matches `dependencies` and `[dev-dependencies]` matches `devDependencies`. The name, version and edition live under `[package]`."),
        ("Read each requirement", "`serde = \"1.0.200\"` allows `>=1.0.200, <2.0.0`. `itoa = \"=1.0.11\"` allows only 1.0.11, and `pretty_assertions = \"1\"` any 1.x release."),
        ("Compare with evidence", "Compiled with plain rustc, the program prints `invoice outside Cargo`. Built by `cargo run`, Cargo sets `CARGO_PKG_VERSION` and it prints `invoice 0.1.0`."),
    ],
    transfer="Create a project with `cargo new invoice` and run `cargo add itoa`. Compare the requirement written to `Cargo.toml` with the exact version recorded in `Cargo.lock`, and explain when `cargo update` would change it.",
    connections=[("previous", "try/catch vs Result", "Errors as Result values"),
                 ("next", "Promises vs futures", "Lazy futures and an explicit runtime")],
    recall=[
        dict(question="Which versions can each requirement select: `a = \"0.4.1\"`, `b = \"1.2\"` and `c = \"=2.0.3\"`?",
             answer="`a`: `>=0.4.1, <0.5.0`, because the caret treats the first non-zero component as the breaking one. `b`: `>=1.2.0, <2.0.0`. `c`: exactly 2.0.3. npm's `^0.4.1` and `^1.2` allow the same ranges as the first two."),
        dict(question="Which files define the default binary and the library target, and what replaces `npm test`?",
             answer="`src/main.rs` is the default binary and `src/lib.rs` the library; extra binaries go in `src/bin/`. `cargo test` builds the test targets and runs unit tests, integration tests in `tests/` and documentation examples, with no script entry needed."),
    ],
))

# ---------------------------------------------------------------- 17
LESSONS.append(dict(
    id="node-promises-to-futures",
    unit="node-runtime",
    title="Promises vs futures",
    concept="Lazy futures and an explicit runtime",
    minutes=12,
    kind="planned",
    summary="A Promise starts running when it is created; a Rust future does nothing until it is polled, usually by `.await` inside a runtime such as Tokio.",
    rule="Futures are lazy: calling an `async fn` only creates a future, and no code inside it runs until something polls it.",
    explanation=[
        "Calling an async function in JavaScript runs its body synchronously up to the first `await`, and the event loop keeps the rest going. That is why the example prints `fetching` before `created`, and why the unused second call still logs. Calling a Rust `async fn` runs nothing: it returns a value that implements `Future`, a state machine waiting to be polled. Only polling, normally through `.await`, executes the body.",
        "Rust has no built-in event loop. Something must poll the top-level future: an executor such as the Tokio runtime behind `#[tokio::main]`, or, in this example, a ten-line `block_on` that polls in a loop. That `block_on` only suits futures that never wait on I/O; a real runtime parks the thread and uses the `Waker` to resume work when a socket or timer is ready. `.await` itself is only allowed inside `async` functions and blocks (E0728).",
        "Laziness has consequences you can use. A future that is dropped before it completes simply stops, which is how timeouts and `select!` cancel work, whereas a JavaScript promise cannot be cancelled from outside; there is only an `AbortSignal` the callee may honour. Writing `let pending = fetch_price();` and awaiting it later starts nothing early. To run several futures concurrently, combine them with `join!` or spawn them as tasks, the counterparts of `Promise.all` and of starting promises without awaiting them.",
        "rustc helps with the most common mistake. A future that is created and never used triggers the `unused_must_use` warning, unused implementer of `Future` that must be used. Treat that warning as an error in async code; it almost always means a missing `.await`.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        async function fetchPrice() {
          console.log("fetching"); // runs as soon as fetchPrice() is called
          return 42;
        }

        const pending = fetchPrice();
        console.log("created");
        pending.then((price) => console.log(`price = ${price}`));

        const unused = fetchPrice(); // still runs, although nobody awaits it
    '''),
    from_stdout="fetching\ncreated\nfetching\nprice = 42\n",
    from_caption="Each call starts the async body immediately, so `fetching` prints twice even though one promise is never used.",
    example=code(r'''
        use std::future::Future;
        use std::pin::pin;
        use std::task::{Context, Poll, Waker};

        async fn fetch_price() -> u32 {
            println!("fetching");
            42
        }

        // A minimal executor for futures that never wait; real programs use a runtime such as Tokio.
        fn block_on<F: Future>(future: F) -> F::Output {
            let mut future = pin!(future);
            let mut cx = Context::from_waker(Waker::noop());
            loop {
                if let Poll::Ready(value) = future.as_mut().poll(&mut cx) {
                    return value;
                }
            }
        }

        fn main() {
            let pending = fetch_price();
            println!("created");
            println!("price = {}", block_on(pending));
            let _unused = fetch_price();
        }
    '''),
    example_stdout="created\nfetching\nprice = 42\n",
    example_caption="`created` prints before `fetching`: the future runs only when `block_on` polls it, and the unused one never runs.",
    contrasts=[
        ("`fetchPrice()` runs the body up to the first `await` immediately.",
         "`fetch_price()` runs nothing; the body starts on the first poll."),
        ("The event loop is built into Node.js.",
         "An executor such as Tokio must poll the top-level future."),
        ("A promise that nobody awaits still runs to completion.",
         "A future that is never polled never runs, and dropping it cancels it."),
        ("`Promise.all([a, b])` runs promises concurrently.",
         "`join!(a, b)` polls both futures concurrently inside one task."),
    ],
    credits=["concurrency/futures"],
    practice=code(r'''
        async fn save(record: &str) {
            println!("saved {record}");
        }

        fn main() {
            save("invoice-7");
            println!("done");
        }
    '''),
    practice_expect={"stdout": "done\n", "warnings": ["unused implementer of `Future` that must be used"]},
    question="What does the practice program print?",
    answers=[
        "`saved invoice-7` then `done`, like calling an async function in Node.js",
        "Only `done`: the future returned by `save` is never polled",
        "Nothing: rustc rejects calling an `async fn` without `.await`",
    ],
    correct=1,
    feedback="The call creates a future and drops it at the end of the statement. rustc warns that it must be used, but the program builds and prints only `done`.",
    task="Predict the output of the example, then move `println!(\"created\")` after the `block_on` call and predict again. Finally replace `let _unused = fetch_price();` with `fetch_price();` and read the warning.",
    success="Your predictions match the program: `created` before `fetching`, and the unused future never prints.",
    misconception="“Calling an `async fn` starts it in the background, like calling an async function in Node.js.”",
    correction="Calling an `async fn` only builds a future. Nothing runs until it is polled, normally by `.await` inside a runtime.",
    trace=[
        ("Create the future", "`let pending = fetch_price();` stores a future. No line inside `fetch_price` has run yet."),
        ("Poll it", "`block_on(pending)` polls once. The body prints `fetching` and returns `42` without waiting, so the first poll is already `Ready`."),
        ("Compare with evidence", "Run it: `created`, `fetching`, `price = 42`. The `_unused` future is dropped at the end of `main` without printing anything."),
    ],
    transfer="Write `async fn total() -> u32` that awaits `fetch_price()` twice and adds the results. Run it with `block_on` and predict how many times `fetching` prints, then compare with a JavaScript version that uses `Promise.all`.",
    connections=[("previous", "npm and package.json vs Cargo", "package.json and npm mapped to Cargo"),
                 ("next", "Futures", "async fn, await, and laziness")],
    recall=[
        dict(question="What does this print, and why?",
             code=code(r'''
                 async fn log(n: u32) -> u32 {
                     println!("log {n}");
                     n
                 }

                 fn main() {
                     let a = log(1);
                     let b = log(2);
                     drop(a);
                     println!("end");
                     let _ = b;
                 }
             '''),
             answer="Only `end`. Each call creates a future without running it, `drop(a)` destroys one that was never polled, and `let _ = b;` does not poll the other. In JavaScript both calls would have logged immediately.",
             expect={"stdout": "end\n"}),
        dict(question="Why does Rust need a runtime such as Tokio when Node.js does not?",
             answer="Node.js ships an event loop that runs promise callbacks and I/O. Rust's standard library defines the `Future` trait but no executor, so a library provides one: it polls futures, parks the thread while they are pending, and uses `Waker`s from timers and sockets to resume them. Choosing the runtime is part of the program's design."),
    ],
))
