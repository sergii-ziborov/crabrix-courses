# Practical paths, 5 November 2026

The six audit stages now have a concrete first implementation:

1. **Compiler practice:** 18 existing Basics/Ownership lessons gain typed labs.
2. **Files and data:** five lessons cover buffered input, path boundaries, sandbox
   file effects, validated records, and a labelled Serde Cargo example.
3. **API boundaries:** three lessons cover checked parsing, optional fallible input,
   and flexible borrowed inputs.
4. **Async operations:** three desktop Cargo examples cover JoinSet ownership,
   semaphore backpressure, and persistent shutdown state.
5. **Reliability:** three labs cover properties and independent oracles, adversarial
   parsers, and a Unicode regression.
6. **WASM/WASI:** three lessons and small compiler labs separate imports, memory
   ranges, and resource budgets from the actual runtime's enforcement.

There are 17 new lessons, 31 new protected compiler labs (18 existing + 13 new),
771 lessons/steps in seven courses, and 46 unchanged example projects. Four new
readings intentionally remain explanation/question exercises: Serde and the three
Tokio examples need their declared Cargo profile. They are not advertised as
dependency-free local labs. The earlier Async Runtime example now uses an explicit
current-thread executor and only the `rt` feature, and the dependency lesson labels
its macro requirements.

The original 754 identities, per-unit positions, questions, answers, and correct
answer positions are frozen in `baseline.json`. Appended units do not reorder old
content. Published content versions increase; old installed repositories and user
projects remain immutable. This is a first practical expansion, not conversion of
all conceptual lessons or a claim that every desktop ecosystem tool runs on WASI.

## Verification

```sh
python3 editorial/practice_20261105/apply.py
python3 tools/complete_lesson_illustrations.py
python3 tools/recompute_digests.py basics ownership projects concurrency systems
python3 editorial/practice_20261105/verify.py
python3 editorial/practice_20261105/verify_readings.py
python3 -m unittest discover -s tests
python3 tools/coursepack.py validate --courses courses --schema schemas
```

`apply.py` uses rustfmt for phone-width reading examples. Diagrams use the existing
deterministic code → rule renderer, retaining custom earlier artwork. Reference
solutions, wrong submissions and compiler receipts live only under `editorial/`;
they are not starter-project files. Installed labs use the existing signed v1
challenge transport and private main, with per-run verdict nonces in the app.
The learner's supplied function has a real typed contract; checks do not depend on
its parameter names. A normal stdout print and early process exit cannot complete
the nonce-protected harness.

`verification.json` records 31 desktop reference passes and 93 rejected compiled
submissions: unchanged, wrong-result, and forged public verdict for every lab.
`reading-verification.json` records all 17 complete examples running with real
dependencies. `Cargo.lock` records the exact desktop verification graph, including
Tokio 1.54.1, Serde 1.0.228, and serde_json 1.0.154. No server executes learner code.
The app repository's `PracticalCourseUpdateTests` runs the 31 actual harnesses in
its bundled wasm compiler and qualifies the production-signed update separately.

Finite cases are evidence for these contracts, not formal proofs, a performance
bound, an exploit-proof grading system, or a production sandbox implementation.
The path and import labs explicitly model only part of the real host boundary.

## Primary references

- [BufRead](https://doc.rust-lang.org/std/io/trait.BufRead.html)
- [Path](https://doc.rust-lang.org/std/path/struct.Path.html)
- [FromStr](https://doc.rust-lang.org/std/str/trait.FromStr.html)
- [Option::transpose](https://doc.rust-lang.org/std/option/enum.Option.html#method.transpose)
- [Serde derive](https://serde.rs/derive.html)
- [Tokio JoinSet](https://docs.rs/tokio/1.54.1/tokio/task/struct.JoinSet.html)
- [Tokio Semaphore](https://docs.rs/tokio/1.54.1/tokio/sync/struct.Semaphore.html)
- [Tokio shutdown](https://tokio.rs/tokio/topics/shutdown)
- [Rust wasm32-wasip1](https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html)

No copied prose or precompiled execution payload is added to the lesson packs.

## Filesystem verification patch

Projects 1.0.9 independently removes any stale test file, calls the learner, and
reads the resulting file from the private harness for every case. It also requires
an error when the destination is a directory. A solution that merely returns the
input text is the regression mutant and is rejected. Verification receipts now bind
the exact reference, starter, harness and mutant through a contract SHA-256.
The 771 web readings remain byte-equivalent as structured content; only app-private
grading data and its pack/version digests change. Published 1.0.8 assets are retained.
