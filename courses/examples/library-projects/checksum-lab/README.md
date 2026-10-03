# Checksum Lab

Compute a deterministic FNV-1a content fingerprint.

## What to notice

FNV-1a folds bytes into one reproducible fingerprint. Find the XOR and multiply operations inside the byte loop, then change one byte and compare the result. A checksum detects changes; it is not a password hash.

## Concepts

- bytes
- wrapping
- hash

## Your challenge

Hash several project files in sorted path order so renaming or editing any file changes one project fingerprint.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
