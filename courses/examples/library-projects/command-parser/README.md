# Command Parser

Turn terminal text into a typed command enum.

## What to notice

Raw text is converted to a typed command enum. Read the branch that recognizes a valid command and the branch that rejects unknown input. Downstream code can then match explicit states instead of interpreting strings again.

## Concepts

- enum
- Result
- splitn

## Your challenge

Add quoted task titles and return a precise error for an unfinished quote.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
