# Palindrome Inspector

Normalize Unicode text before comparing it.

## What to notice

Text is normalized before its characters are compared in both directions. Inspect exactly which case, spacing, punctuation, and Unicode rules the implementation applies. Try inputs that challenge each rule.

## How it works

`normalized` filters characters with `is_alphanumeric`, applies Unicode lowercase mapping, and collects a new string. `is_palindrome` then compares the normalized characters forward and backward without constructing a second reversed string. Trace a phrase with spaces and punctuation to see why those marks disappear before comparison. Try a Unicode case mapping and inspect the exact output; text normalization is more nuanced than simply lowering ASCII letters, and this function does not implement every linguistic equivalence.

## Concepts

- chars
- filter
- reverse

## Your challenge

Return the normalized text with the verdict and add three more punctuation-heavy test phrases.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
