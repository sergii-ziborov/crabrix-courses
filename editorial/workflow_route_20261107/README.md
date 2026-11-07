# Git → CLI → HTTP → SQL → diagnostics → delivery

Projects 1.1.0 is an authoring candidate for Crabrix 1.1.8 and the new
workflow-terminal-v1 capability. It adds 24 lessons in six ordered units to
Cargo & Real Projects. The complete authored snapshot contains 798 lessons and
stages: 198 Rust lessons and 600 Atlas stages. The existing 46 Examples and every
previous lesson, answer position and unit prefix are retained.

Each lesson contains substantive explanation, a complete worked Rust program,
a separate reading question, a typed solution.rs starter, independent verification
caller, contextual diagram and transfer task. The native SQL labs execute the
student's DDL or query against real SQLite fixtures; they accept equivalent SQL
and reject constraint, wildcard and partial-transaction regressions. Their
sqlite-v1 profile creates a fresh database for each graded invocation. The
website's SQL reading examples print the statement and explicitly distinguish
that demonstration from executing the native database lab.

The shared Task Ledger companion is source/data under
courses/projects/projects/route-git-review/companion. All 24 lessons point to it
through workflow-companion.json. Open Task Ledger creates a new personal project,
independent of compiler-lab progress, course replacement and other project copies.
It contains a std-only on-device CLI/HTTP adapter program and a separate complete
Axum/SQLx/SQLite desktop server with Cargo.lock, Dockerfile, CI, acceptance probe
and artifact verification script. The mobile and desktop target profiles are
labelled; no Docker or arbitrary Linux process is claimed to execute on iOS.

## Reproduce the source and desktop checks

```sh
python3 editorial/workflow_route_20261107/author.py
python3 editorial/workflow_route_20261107/verify.py
python3 tools/complete_lesson_illustrations.py
python3 tools/recompute_digests.py projects
python3 tools/coursepack.py validate --courses courses --schema schemas
python3 -m unittest discover -s tests
cargo test --locked --manifest-path editorial/workflow_route_20261107/companion/local/Cargo.toml
cargo test --locked --manifest-path editorial/workflow_route_20261107/companion/desktop/Cargo.toml
python3 editorial/workflow_route_20261107/companion/desktop/scripts/acceptance.py
```

verification.json binds each reference, starter, semantic regression and private
caller to a SHA-256. All 24 readings execute; 24 reference solutions pass; the
72 unchanged, wrong and forged-verdict variants fail. These are finite desktop
contracts, not a formal proof or the native runtime qualification. The desktop
acceptance probe exercises actual HTTP requests, exact retry replay, conflicting
keys, invalid input, injection-shaped data, graceful stop and data after restart.
The native gate belongs to the Crabrix application repository and must be run
separately with its shipped compiler and host bridge.

## Native package gate without production credentials

Build the deterministic packs, sign only the Projects descriptor with the openly
published tests/keys/test-publisher.seed using tools/sign_release.py and
--allow-test-key, then place the Projects ZIP, descriptor and test-keyring.json in
the application's ignored CrabrixTests/CompilerCandidate/WorkflowPack directory.
That key is trusted only by the explicit test installer, never the product keyring.
Export the private QA fixture with:

```sh
python3 editorial/workflow_route_20261107/export_native_fixture.py --out /path/to/CrabrixTests/CompilerCandidate/WorkflowRoute.json
```

Run WorkflowRouteTests, ProjectTerminalSessionTests, SyntaxHighlighterTests,
CoursePackVerifierTests and GitWorkspaceTests on an iOS Simulator. The route gate
checks all 24 typed contracts, real SQLite, fresh CLI input across cached builds,
actual loopback HTTP → Rust → SQLite, CLI/HTTP shared data, package installation,
old repository snapshots and the minimum app version. The application record
contains the exact final result; this source receipt does not substitute for it.

No signed production catalog, public release asset or pending App Review build
is changed by this authoring candidate. Production publication must wait for the
compatible application release and its independent qualification. A container
build and physical-device performance/layout are separate checks.
