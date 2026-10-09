# Crabrix Courses

The complete, versioned educational corpus for [Crabrix](https://github.com/sergii-ziborov/Crabrix): seven Rust and Algorithms courses, their native lesson data, checks, editable starter source, and a separate downloadable Examples gallery.

The baseline contains 48 units and 742 lessons, including the 200-pattern Algorithm Atlas with 600 ordered steps. It also preserves 46 authored Academy Examples and 358 term pairs. All example metadata, Rust source trees, and individual README files are under `courses/examples/library-projects/` and ship in the signed Examples CoursePack. The 46 READMEs now include a project-specific explanation that the app shows before the source preview. Four examples include local diagrams under `courses/examples/media/`. The gallery downloads separately from Cargo & Real Projects; selecting an example creates an editable project copy with its own ID and pack-version provenance. [The inventory](migration/inventory-summary.json), [original parity report](migration/parity-report.json), and [current parity report](migration/parity-report-current.json) record the original and current layouts. The current parity report records these editorial changes separately; original lesson data and example Rust source remain equal.

The six Rust courses contain 142 lessons. On the `codex/deeper-lessons` authoring branch, each has at least twice the original explanatory word count, and at least every other lesson has a generated diagram with alt text and a caption. The expanded copy is live on the [free Learn website](https://crabrix.com/learn/). The 600 Algorithm Atlas steps retain their earlier text. App downloads still use the last signed catalog until new production-signed CoursePacks are released; changed authoring files are not a signed release.

## Format and delivery

Each course is authored under `courses/<id>/` and packaged as one CoursePack v1 ZIP. `manifest.json` inventories every payload file by byte length and SHA-256; it never hashes itself. An external signed descriptor binds the archive digest, version, compatibility, and course identity. The separately signed catalog has a monotonic sequence. Ed25519 signs exact payload bytes with distinct descriptor and catalog prefixes.

Packs contain JSON lesson/check data and editable Rust sources. They cannot carry runtime/compiler updates or executable validator plugins. The publisher's private key is kept outside this repository. `keys/production-keyring.json` contains only the public verification key. `tests/keys/` contains an openly published test key for fixtures only.

## Build and verify

Python 3.11+ and `cryptography` are required for signature verification. From the repository root:

```sh
python3 tools/coursepack.py inventory --baseline migration/baseline-inventory.json --out migration/inventory-summary.json
python3 tools/coursepack.py validate --courses courses/ --schema schemas/
python3 tools/coursepack.py build --courses courses/ --out dist/ --deterministic
python3 tools/coursepack.py parity --legacy migration/baseline-inventory.json --packages dist/ --out migration/parity-report-current.json
python3 tools/coursepack.py verify --descriptor dist/basics.descriptor.json --archive dist/basics-1.0.1.zip --keys keys/production-keyring.json
python3 tools/coursepack.py verify --descriptor dist/examples.descriptor.json --archive dist/examples-1.0.2.zip --keys keys/production-keyring.json
python3 tools/coursepack.py verify-catalog --catalog catalog.v1.json --keys keys/production-keyring.json --last-sequence 4
python3 -m unittest discover -s tests
```

The signed descriptors in the release are bound to the exact archive bytes. If local authoring content changes, sign a new version; an old descriptor must fail verification. The `verify` command rejects bad signatures, mismatched ZIP digests, path traversal, links, duplicate names, extra files, and size-limit violations before installation. The app installer adds the atomic staging and progress-preservation gates.

## Rebuild from the legacy source

In the Crabrix app repository, `bash migration/export_legacy.sh` executes the curriculum models and writes the fixture. This is a migration tool, not a second production content engine. For a new empty authoring tree:

```sh
python3 tools/coursepack.py import-legacy --baseline migration/baseline-inventory.json --courses courses/
```

The file layout and invariants are described in [MIGRATION.md](MIGRATION.md) and [PROVENANCE.md](PROVENANCE.md). The app's download and offline behavior belongs to its separate integration release.

## Rights

The tools and schemas are MIT licensed under [LICENSE](LICENSE). Course texts, checks, projects, and assets remain author owned under [CONTENT-LICENSE.md](CONTENT-LICENSE.md); public access is not an MIT grant for the corpus. Contributions follow [CONTRIBUTING.md](CONTRIBUTING.md).
