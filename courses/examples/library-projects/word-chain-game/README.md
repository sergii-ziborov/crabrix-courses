# Word Chain Game

Validate turn order and reject repeated words.

## What to notice

Repeated-word and adjacent-letter checks determine whether a sequence is valid. The variable named `good` is not actually a valid chain: `borrow` ends in `w`, while `rust` starts with `r`. Predict the first error for both supplied arrays, then try the valid chain `crab`, `borrow`, `wolf`, `fish`.

## How it works

The validator first inserts lowercase copies of all words into a `HashSet` and rejects a repeated word. It then examines adjacent pairs with `windows(2)`, requiring the last character of one word to equal the first character of the next. Both supplied arrays return errors: `good` has a broken `borrow` to `rust` connection; `bad` repeats `rust`, so it fails the uniqueness pass before the connection pass. Duplicate detection ignores case, but the boundary-character comparison uses the original spelling. Try changing a word's capitalization to see those two rules diverge; there is no interactive turn-taking in this project.

## Concepts

- HashSet
- windows
- validation

## Your challenge

Return a typed error that distinguishes duplicate words from a broken letter connection.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
