#!/bin/sh
set -eu
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo 'Commit the reviewed source before producing a revision-bound release.' >&2
    exit 2
fi
cargo fmt --check
cargo test --locked
cargo build --locked --release
mkdir -p release
cp target/release/task-ledger-server release/task-ledger-server
# Record the exact checkout and the bytes that will be delivered.
git rev-parse HEAD > release/source-revision.txt
rustc -vV > release/toolchain.txt
if command -v sha256sum >/dev/null 2>&1; then
    (cd release && sha256sum task-ledger-server > SHA256SUMS && sha256sum -c SHA256SUMS)
else
    (cd release && shasum -a 256 task-ledger-server > SHA256SUMS && shasum -a 256 -c SHA256SUMS)
fi
