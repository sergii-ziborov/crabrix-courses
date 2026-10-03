# Checksum Lab

Compute a deterministic FNV-1a content fingerprint.

## What to notice

FNV-1a folds bytes into one reproducible fingerprint. Find the XOR and multiply operations inside the byte loop, then change one byte and compare the result. A checksum detects changes; it is not a password hash.

## How it works

FNV-1a starts with a fixed 64-bit offset basis. For each input byte, the loop XORs that byte into the running value and multiplies with wrapping arithmetic by a fixed prime. The result is printed as sixteen hexadecimal digits. `rust` and `Rust` have different bytes, so they produce different fingerprints. The same bytes always reproduce the same value, but collisions are possible and this fast non-cryptographic hash is unsuitable for passwords or signatures.

## Concepts

- bytes
- wrapping
- hash

## Your challenge

Hash several project files in sorted path order so renaming or editing any file changes one project fingerprint.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
