# Academy corrections — 27 October 2026

This pass covers all 200 Algorithm Atlas patterns (including the remaining 90
from the earlier audit), their 600 lesson steps and eight Rust lessons. Lesson,
unit and project IDs and existing correct-answer positions are preserved.

## Authored changes

- Each algorithm now has its own complete, std-only Rust worked program, a
  numerical trace and a pattern-specific concept question. Recognition and
  challenge questions use separate fixtures: 600 distinct question prompts.
- Each challenge has five distinct semantic inputs plus two surrounding-space
  variants. Private harnesses accept any valid Two Sum pair and any valid peak;
  they reject repeated indices, wrong sums and non-peaks. Linked-list
  intersection now explicitly constructs a shared Rc tail and compares identity.
- Imos inclusive range updates remove at R+1; its maximum is 5. Shipping weights
  1 through 10 in three days needs capacity 21. Reservoir sampling specifies the
  replacement decision; stock span explicitly includes today. Input domains,
  deterministic ordering, canonical outputs and implementation costs are stated.
- Pin/Unpin, panic versus unwind/abort, cfg parsing, additive Cargo features,
  future cancellation, PostgreSQL composite-index eligibility, growth classes,
  PhantomData layout and rustdoc wording are corrected. Two replacement
  ImageGen diagrams show the Pin contract and range structures, including Imos.

## Reproduce

```sh
python3 editorial/academy_20261027/verify_examples.py
python3 editorial/academy_20261027/verify_harnesses.py
python3 -m unittest discover -s tests -v
python3 tools/coursepack.py validate --courses courses --schema schemas
```

`oracles.py` adds 90 independent reference calculations to the previous 110.
`rust_sources.py` contains the individual typed cores; `fixtures.py` builds typed
calls; `examples/` contains 200 standalone programs. `teaching.py` records the
authored concept questions and concrete traces. `publish_content.py` applies
the changes reproducibly against the immutable pre-pass revision 52b6751.
`fix_rust_lessons.py` records the eight Rust corrections. The two image prompts,
edits and final source-image paths are recorded in `imagegen-prompts.json`.

## Evidence and limits

- `example-verification.json`: 1,000 Rust tests passed against independently
  calculated results on rustc 1.99.0, aarch64 macOS. This includes all 200 patterns.
- `harness-verification.json`: 402 harness tests passed, covering all 200 packaged
  harnesses, 1,400 calls, rejection of deliberately wrong results and acceptance
  of alternative valid Two Sum/peak results.
- Harness verification uses typed implementations behind a known-fixture input
  adapter. It tests the packaged checker and algorithm results; it does not
  claim to test a universal learner-written text parser.
- Finite fixtures are regression evidence, not a proof of every algorithm for
  all inputs or of its asymptotic bound. These are desktop semantic checks,
  not an iPhone performance measurement. Preconditions bound arithmetic, valid
  graph/tree shapes and ASCII string inputs unless a task states otherwise.

## Native distribution

Catalog sequence 15 updates Algorithms 1.0.6, Ownership 1.0.6, Projects 1.0.6,
Concurrency 1.0.5, Systems 1.0.6 and Interview 1.0.8. Basics 1.0.6 and Examples
1.0.4 retain their existing assets and URLs. Archives and descriptors are signed
with an existing trusted production key; no keyring or application code changes
are needed. The application's actual Swift verifier and planner accepted the six
archives, a partial update, replay rejection and archive-tamper rejection.

After publication, open Learn, refresh courses and choose **Update all**. An
already open lesson retains its pinned old snapshot until it is closed. User
projects remain separate from course material. The website pins the committed
authoring snapshot and privately serves the same lesson and image bytes.
