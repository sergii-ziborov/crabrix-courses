# Academy migration

The baseline source identity is
`c38423e7503a56d6cd97e3a6c17651d5a5c33d62`, content version `1.0.1`.
The Swift exporter was run locally on 30 September 2026. It did not compile
student answers. The resulting fixture recorded 7 courses, 48 units, 742 lessons,
200 Atlas patterns, 200 challenges, 46 Academy Examples, and 358 term pairs.

The initial `1.0.0` release omitted 99 base Term Train pairs from its export.
It remains immutable for audit. Version `1.0.1` and catalog sequence 2 include
the full executed `TermTrainDeck.all` corpus plus Algorithm Atlas terms.

`migration/parity-report.json` records semantic equality after rebuilding packs:
`missing=0`, `unexpected=0`, `unapprovedChanges=0`. This gate checks migration
fidelity; it does not certify every algorithm answer.

The later [current parity report](migration/parity-report-current.json) checks
the standalone Examples pack against the same immutable baseline. It records
the 46 authored README expansions and four local illustrations as approved
editorial changes while comparing every original lesson, answer, validator,
example Rust source, ID, and order.

The app-side installed reader, transition resources, progress migration, and
download lifecycle are separate integration gates. Content parity alone does
not establish that those gates pass.
