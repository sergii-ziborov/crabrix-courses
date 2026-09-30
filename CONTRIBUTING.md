# Contributing

Edit the authoring tree under `courses/<courseID>/`. Keep stable IDs, order,
existing explanations, answer options, and checks unless the change is an
intentional content revision. A published `(courseID, language, contentVersion)`
is immutable; increment `contentVersion` for corrections.

Run `python3 tools/coursepack.py validate --courses courses/ --schema schemas/`
and `python3 -m unittest discover -s tests` before a pull request. The signing
step is restricted to release maintainers. Pull requests never receive the
production key.

New content or validator kinds require an app capability review. CoursePacks
contain data and editable Rust source, not executable plugins, compiler updates,
or precompiled Wasm artifacts.
