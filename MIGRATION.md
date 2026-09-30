# Academy migration

The baseline source identity is
`c38423e7503a56d6cd97e3a6c17651d5a5c33d62`, content version `1.0.0`.
The Swift exporter was run locally on 30 September 2026. It did not compile
student answers. The resulting fixture recorded 7 courses, 48 units, 742 lessons,
200 Atlas patterns, 200 challenges, 46 gallery projects, and 259 term pairs.

`migration/parity-report.json` records semantic equality after rebuilding packs:
`missing=0`, `unexpected=0`, `unapprovedChanges=0`. This gate checks migration
fidelity; it does not certify every algorithm answer.

The app-side installed reader, transition resources, progress migration, and
download lifecycle are separate integration gates. Content parity alone does
not establish that those gates pass.
