# Language bridges — authoring contract (23 November 2026)

Two new courses for developers who already program in another language:

| Course ID | Title | Comparison language |
|---|---|---|
| `rust-for-c-developers` | Rust for C Developers | C17 |
| `rust-for-nodejs-developers` | Rust for Node.js Developers | JavaScript (Node.js 22) and TypeScript |

The course ID is also the public URL: `crabrix.com/learn/rust-for-c-developers/<lesson-id>/`.

Every bridge lesson shows one habit from the other language next to the Rust
equivalent, names the differences precisely, and proves the learner can write
the Rust side. Completing a bridge lesson **credits** existing Academy lessons
whose rule it already taught and checked, so an experienced C or Node.js
developer does not have to walk through "Variables" or "Loops" one by one.

## Lesson file

A bridge lesson is an ordinary CoursePack lesson (same fields as
`courses/basics/lessons/*.json`) plus one `bridge` object:

```json
"bridge": {
  "from": "c",
  "fromLabel": "C",
  "fromCode": "#include <stdio.h>\n...",
  "fromCaption": "One sentence on what the C code does and the habit it shows.",
  "contrasts": [
    { "from": "`free(p)` is a call you must remember on every path.",
      "rust": "The owner's scope ends and `Drop` runs exactly once." }
  ],
  "credits": ["ownership/ownership", "ownership/drop-order"]
}
```

- `from`: `"c"`, `"javascript"` or `"typescript"`. `fromLabel` is display text
  (`"C"`, `"JavaScript (Node.js)"`, `"TypeScript"`).
- `fromCode`: a complete program or module, at most 30 lines, that really
  compiles/runs (see Verification). Prefer a complete C program with `main`.
- `contrasts`: 2–4 rows. Each row is one concrete difference; inline code in
  backticks; no marketing language. Both cells at most 160 characters.
- `credits`: 0–4 `"courseID/lessonID"` strings (0 only for general theory lessons) from `basics`, `ownership`,
  `projects`, `concurrency` or `systems`. Never `interview` or `algorithms`.
  Credit a lesson only if this bridge lesson teaches that lesson's
  `writing.rule` **and** its check (quiz or compiled challenge) tests the
  Rust-specific part of it. When in doubt, do not credit. A target lesson is
  credited by at most one lesson of the same bridge course.
- The Rust side is the lesson's normal `writing.exampleCode` /
  `writing.exampleCaption`. For bridges it must be a complete program with
  `fn main()` that compiles verbatim.
- `writing.practiceCode`: the other language's habit written in Rust, the way
  a newcomer would first try it, so the learner sees the actual rustc error
  (e.g. `E0382`, `E0384`, `E0502`) or the panic. Record the exact code.
- Lesson IDs are global across the whole catalog (progress is one flat set),
  so every ID starts with `c-` or `node-`.
- Required fields as in existing lessons: `id`, `parentID`, `order`, `title`,
  `concept`, `minutes` (8–14), `exerciseKind`, `writing` (summary, explanation
  with paragraphs separated by a blank line, exampleCaption, exampleCode,
  task, success, rule, practiceCode, question, answers [3–4], correctAnswer,
  feedback, recall [exactly 2]), `depth` (traceSteps 3, misconception,
  correction, transferChallenge, connections 1–2). Leave `contentDigest` and
  `illustration` out; tooling adds both (a deterministic side-by-side PNG).
- Even backtick count in every prose field. No `core idea` in recall questions.
- `correctAnswer` positions must vary across the course (not always 0).

## Exercise and check

- Use `exerciseKind: "runnable"` with a compiled challenge whenever the topic
  can run in the app compiler: Rust std only, `wasm32-wasip1`, single thread,
  no files, processes, network, `extern` linking, or crates. The check file
  then has `challenge` and `evidence.kind = "algorithmChallenge"` exactly like
  `courses/basics/checks/option-result.json`, and the starter lives in
  `projects/<lesson-id>/project.json` + `solution.rs` (`todo!("implement the
  contract")` stub, same text as `challenge.source`).
  The challenge is a port: "this C/JS function, written in Rust". At least
  three verification cases (visible, boundary, semantic).
- Topics that cannot run in the app (threads, FFI linking, async runtimes,
  Cargo/npm commands) use `exerciseKind: "planned"` with
  `evidence = {"kind": "reasoning", "correctAnswer": N}` equal to
  `writing.correctAnswer`.
- Aim for at least 60% runnable lessons per course.
- The app compiler is Rust 1.96 (`wasm32-wasip1`): compile every Rust source
  with both `~/.rustup/toolchains/1.89.0-aarch64-apple-darwin/bin/rustc` and
  `~/.rustup/toolchains/1.100.0-aarch64-apple-darwin/bin/rustc`,
  `--edition=2024`.

## Verification (must be reproducible)

Each course has `editorial/bridges_20261123/<course-id>/verify.py`, run with
`python3 -I`, writing `verification.json` next to it. It must:

1. compile and run every `writing.exampleCode` with both rustc versions and
   record stdout;
2. compile every `writing.practiceCode` and record the expected outcome
   (`error[E…]` code list, or the panic message) — assert it really fails the
   way the lesson says;
3. C: `clang -std=c17 -Wall -Wextra` and run `fromCode`; when a lesson shows
   undefined behaviour, also run it with `-fsanitize=address,undefined` and
   record the sanitizer finding the prose relies on. JavaScript:
   `node` 22 runs it. TypeScript: type-check with
   `/Users/serhiirihgt/dev/crabrix-poc/site/node_modules/.bin/tsc --strict
   --noEmit --target es2022 --module nodenext`, then run with
   `node --experimental-strip-types`;
4. for every runnable lesson: the stub + harness compiles and fails; a
   reference solution (kept in `editorial/.../solutions/<lesson-id>.rs`, not
   in the pack) + harness prints exactly `expectedOutput`; at least one
   plausible wrong port (e.g. C-style wrapping arithmetic) is rejected;
5. assert every credit target exists, and every lesson field rule above.

Write work files under `build/bridges-20261123/<course-id>/` (gitignored).

## Course files

`courses/<course-id>/course.json`, `units/*.json`, `lessons/*.json`,
`checks/*.json`, `projects/<id>/…`, `terms.json` (8–16 pairs: `term` is the
Rust term, `description` explains it through the other language's nearest
equivalent, `topic` is a bridge lesson ID), `provenance.json`
(`editorialRevision: "bridges_20261123"`). `contentVersion` `1.0.0`. Units: 3–5 (a first general theory unit is allowed),
each 3–6 lessons. Course pack requires capability `bridge-lessons-v1`.

## Credit semantics (app)

- A credited lesson counts as done for unlocking, Continue learning and course
  progress, and is shown as "Known from C" / "Known from Node.js".
- It does not award XP or achievements; only a real completion does.
- Its recall cards join Flashcards, so spaced repetition checks the credit.
- Completing a credited lesson normally turns it into a regular completion.
