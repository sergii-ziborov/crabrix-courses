#!/usr/bin/env python3
"""Write CREDITS.md from the course files: one line per credit with the target's rule."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
COURSE = REPO / "courses" / "rust-for-c-developers"
HOW = {
    "basics/hello-rust": "explanation P2/P4 (`!` = macro expanded at compile time; `fn main`); quiz: the two-placeholder program is rejected during macro expansion; challenge builds the label with `format!`",
    "basics/print-formatting": "explanation P2–P3; quiz: a missing argument is a compile error; challenge `label` needs `{:>8}`, `{:03}`, `{:#06x}` (the `{:8}` port is rejected)",
    "basics/variables": "explanation P1–P3 (`mut`, `E0384`, shadowing); quiz: `let total = 0; let total = total + 5; total += 1;` → the `+=` is rejected because the shadowing binding is not `mut` (probe-verified)",
    "basics/number-types": "explanation P1 (no implicit integer conversions, `From`/`TryFrom`); quiz: `d < u` on `i32`/`u32` is `E0308`; challenge `to_byte` must use a checked conversion",
    "basics/operators": "explanation P2–P4 (debug panic vs release wrap, `checked_`/`wrapping_`/`saturating_`, `as`); challenge `total_bytes` must return `None` on overflow — wrapping and plain `*` ports are rejected in debug and release",
    "basics/functions": "explanation P1/P3 (tail expression is the return value); quiz: the trailing `;` after the `if` makes the body `()` (`E0308`); challenge wrong port with a trailing `;` fails to compile",
    "basics/block-expressions": "explanation P3 (semicolon turns a tail value into `()`); same quiz; recall card 1 (`x * 3;` block evaluates to `()`) is compiler-verified",
    "basics/loops": "explanation P1/P3 (`for` over collections/ranges, `loop` with `break value`); quiz computes a `loop { break n }` value; challenge `first_power_at_least` uses a loop with a value",
    "basics/ranges": "explanation P2 (`..` excludes, `..=` includes, safe at `u8::MAX`); quiz sums `found..=7`; challenge `count_multiples(250, 255, 5)` rejects `lo..hi + 1` and `lo..hi` ports",
    "ownership/ownership": "explanation P2–P3 (one owner, moves, `E0382`); practice shows `E0382`; challenge `take_largest` must move the winning buffer (pointer-identity check rejects the `.cloned()` port)",
    "ownership/drop-order": "explanation P4 (reverse declaration order); quiz: `_log`, `_lock`, `_file` drop as file, lock, log (probe-verified); example prints the order",
    "basics/references-intro": "explanation P2/P4 (`&T` lends read-only access, caller keeps ownership); challenge `append_doubled(dst, src: &[i32])` — harness reuses `src` after the call",
    "ownership/borrowing": "explanation P2–P3 (many `&T` or one `&mut T`, `E0502`, borrows end at last use); quiz on `let first = &v[0]; v.push(2)`; practice and aliasing probe both `E0502`",
    "ownership/slices": "explanation P2–P3 (slice = pointer + length, a view, no allocation); quiz: `-> &[i32]` is a borrowed view tied to the input; challenge `longest_run` returns a subslice (pointer checked)",
    "ownership/lifetimes-intro": "explanation P2–P4 (annotation relates borrows, never extends one; elision; `E0106`, `E0597`); quiz: two reference inputs need an annotation (probe `E0106`); challenge rejects tying `prefix` to `'a` (`E0597`)",
    "ownership/copy-clone": "explanation P2–P4 (`Copy` only for resource-free types, `E0204`, explicit `.clone()`); quiz: why `Path { Vec }` cannot be `Copy`; practice `E0204`; challenge rejects the shallow-copy port (`E0507`)",
    "basics/structs": "explanation P2 (`&self` reads, `&mut self` modifies, `self` consumes); quiz: `close` must take `self`; practice `E0382` after `finish(self)`; challenge `Budget` methods",
    "basics/methods-intro": "explanation P2–P3 (read the receiver for the ownership effect, auto-borrow at `.`); same quiz; recall maps C prototypes to receivers",
    "basics/enums": "explanation P2–P3 (variants with data, exhaustive `match`, `_` hides new variants); quiz + practice `E0004`; challenge rejects the `_ => 0` port that forgets `Triangle`",
    "basics/pattern-matching": "explanation P4 (bindings, guards, guards do not count for exhaustiveness); quiz: the guarded `Click` arm leaves the variant uncovered (`E0004`); recall card 2 is compiler-verified",
    "basics/option-result": "explanation P2–P3 (`Option` for absence, `Result` when the reason matters); quiz: `Option<&V>` for a lookup, `Result<Config, ParseError>` for a parser; practice `E0308`",
    "basics/recoverable-errors": "explanation P3–P4 (`Result` for expected failures, `?`, `unwrap` only for bugs); same quiz; challenge `parse_port` returns `Result<u16, PortError>` for invalid external text",
    "basics/strings": "explanation P2–P3 (`len()` bytes vs `chars().count()` scalar values); quiz: `\"café\"` → 5 and 4; challenge `initials` must use Unicode `to_uppercase` (the ASCII port is rejected)",
    "basics/chars-and-text": "explanation P4 (no integer indexing because of UTF-8 boundaries, `E0277`); practice `E0277`; challenge `truncate_at_boundary` rejects the `&text[..max_bytes]` port that splits `é`",
    "projects/modules": "explanation P2–P3 (private by default, `pub` exports, `E0603`, `mod name;` loads `name.rs`); practice `E0603`; quiz answer verified with a real Cargo package",
    "projects/package-layout": "explanation P4 (`src/main.rs` binary, `src/lib.rs` library, binary uses the library by package name); quiz: `shapes::geometry::area` — verified with `cargo run` on rustc 1.100.0",
    "systems/unsafe": "explanation P2–P3 (`unsafe` is a claim about invariants, `# Safety` / `// SAFETY:`); quiz: the block claims non-null, aligned, live, initialised",
    "systems/raw-pointers": "explanation P1–P2 (creating raw pointers is safe, dereferencing needs `unsafe`); quiz: only `*p` needs `unsafe` (probes: creating/offsetting compiles, deref is `E0133`); practice `E0133`",
    "concurrency/concurrency": "explanation P2 (`spawn` needs `Send + 'static`, `move`, `E0373`, `thread::scope`); quiz: `move` gives the thread its own `Arc`; practice `E0373`",
    "concurrency/shared-state": "explanation P3 (`Mutex<T>` owns the data, guard unlocks on drop, `Rc` is not `Send`); quiz: the mutex unlocks when guard `n` drops; probe: `Rc` into `spawn` is `E0277`",
    "basics/what-is-rust": "explanation P1 (ahead-of-time rustc → LLVM → native executable, no GC or VM), P3 (types, ownership and borrowing checked before the program runs); quiz: safety comes from compile-time checks, then a native executable; `file` confirms a Mach-O arm64 executable; practice `E0505`",
    "basics/compiler-feedback": "explanation P2–P3 (code, primary `^^^` span, `---` labels, note, help; fix the first error and recompile); quiz: fix the first error at its primary span before later ones; the real E0382 diagnostic's spans, note and help are asserted by verify.py"
}
NOT_CREDITED = [
    "`basics/function-parameters` — taught in c-functions-are-expressions, but no check tests the no-implicit-argument-conversion rule.",
    "`basics/control-flow` — `if` as an expression is taught, but no check tests that all branches share one type.",
    "`systems/ffi` — `repr(C)` and `unsafe extern \"C\"` are taught and compiled in c-unsafe-and-ffi, but its quiz tests the raw-pointer rule, not the `repr(C)` rule.",
    "`ownership/mutable-borrows`, `concurrency/send-sync` — touched in prose only.",
]

lines = ["# Credits — rust-for-c-developers", "",
         "Each line: credited lesson — its `writing.rule` — where the bridge lesson teaches it and which check tests it.",
         "Checks are the lesson's quiz (reasoning evidence) and, for runnable lessons, the compiled challenge;",
         "all compiler claims are verified by `verify.py` (see `verification.json`). Generated by `credits.py`.", ""]
seen = set()
for uid in json.loads((COURSE / "course.json").read_text())["unitIDs"]:
    for lid in json.loads((COURSE / "units" / f"{uid}.json").read_text())["lessonIDs"]:
        lesson = json.loads((COURSE / "lessons" / f"{lid}.json").read_text())
        lines.append(f"## {lid} ({lesson['exerciseKind']})")
        if not lesson["bridge"]["credits"]:
            lines.append("- No credit: a general theory lesson with no matching Academy lesson.")
        for target in lesson["bridge"]["credits"]:
            course, target_id = target.split("/")
            rule = json.loads((REPO / "courses" / course / "lessons" / f"{target_id}.json").read_text())["writing"]["rule"]
            lines.append(f"- `{target}` — {rule} — {HOW[target]}")
            seen.add(target)
        lines.append("")
assert seen == set(HOW), sorted(seen ^ set(HOW))
lines += ["## Considered and not credited", ""] + [f"- {item}" for item in NOT_CREDITED] + [""]
(HERE / "CREDITS.md").write_text("\n".join(lines), encoding="utf-8")
print(f"{len(seen)} credits")
