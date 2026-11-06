# Library Contracts — 6 November 2026

Cargo & Real Projects 1.0.12 adds one unit with three substantive readings:
Evolving a Public API, MSRV Is a Tested Promise, and The Downstream Feature Matrix.
Existing lesson IDs/order, quiz answers and saved-answer positions are retained.
The added lessons each have a complete worked program, an independent reading
question, a separate typed compiler-lab harness, a contextual infographic and a
transfer task. The lab README links to these companion sources.

## Reproduce

Run from the repository root:

```sh
python3 editorial/library_contracts_20261106/verify.py
python3 -m unittest discover -s tests
python3 tools/coursepack.py validate --courses courses --schema schemas
```

The compiler check uses real installed `1.78` and `stable` rustup toolchains.
It records their actual identities in verification.json. It never downloads a
compiler or dependency and does not change the default toolchain. Cargo's fixture
uses edition 2021, resolver 2, local path dependencies and lockfile format 3.

- Six complete reading-program runs pass across the two compilers.
- Twenty-four lab runs compile: references pass; unchanged TODO, wrong behavior
  and a printed forged verdict fail the independent caller.
- Eight separately linked API-consumer cases check the exact same source bytes
  against v1, compatible v2, a changed constructor arity, and changed behavior.
- `Option::is_none_or` succeeds on the current compiler and fails with E0599 on
  Rust 1.78. The match-based implementation passes both compilers.
- The Cargo matrix covers default, no-default, details, trace and their union on
  both compilers. A two-path graph confirms that one edge's default-features=false
  does not disable defaults another edge enables. A behavior change under one
  feature is rejected; duplicate helpers pass separately and fail their union.
- All 31 corpus/package tests pass; eight packs and 774 lessons validate.

The companion `wasm-verification.json` records 13 checks through the current
Crabrix browser Worker and bundled rustc 1.96.0-dev / wasm32-wasip1. Assets were
served locally and checksum-verified; all subsequent network requests were
rejected. Complete readings, typed reference and wrong labs, and four actual
Cargo feature profiles were compiled/executed locally. This is headless Worker
execution, not a screenshot or a physical-device test.

## Boundaries

The local lesson harness grades an API's behavior under the installed compiler.
It does not emulate Rust 1.78 or certify every learner Cargo feature graph. The
separate Cargo/consumer checks are deliberately explicit. Finite fixtures and
mutations do not prove compatibility for every external program or malicious
attempt to bypass an exercise. No backend compilation was added.

App capability review: these are ordinary coursepack-v1 lessons, existing typed
challenge/evidence kinds, standard-library Rust and the existing illustration
format. No executable plugin or new validator is introduced. Optional `resources`
are link metadata for the web reading view; older native decoders ignore unknown
JSON members, and the compiler-lab README carries the companion URL in the app.
The pending App Review binary is unchanged. Variance, HRTB/GAT, unsafe soundness,
full async cancellation, Loom and service capstones remain separate follow-ups.

## Primary references

- [Cargo SemVer compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)
- [Cargo Rust version support](https://doc.rust-lang.org/cargo/reference/rust-version.html)
- [Cargo features](https://doc.rust-lang.org/cargo/reference/features.html)
- [Cargo dependency resolver](https://doc.rust-lang.org/cargo/reference/resolver.html)
- [Option::is_none_or, stabilized in 1.82](https://doc.rust-lang.org/std/option/enum.Option.html#method.is_none_or)

Original lessons and diagrams retain the repository's educational-content licence.
