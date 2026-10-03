# Command Parser

Turn terminal text into a typed command enum.

## What to notice

Raw text is converted to a typed command enum. Read the branch that recognizes a valid command and the branch that rejects unknown input. Downstream code can then match explicit states instead of interpreting strings again.

## How it works

`parse` trims the input and splits it into at most two parts, keeping an `add` title together. A `match` turns recognized text into `Command::Add`, `Command::Done`, or `Command::List`; the numeric argument for `done` is parsed into `usize`. Unknown commands and invalid indices return `Err` instead of an unusable command. The sample loop prints both successes and failures. Try `add` without a title or `done x` and inspect which branch handles each case.

## Concepts

- enum
- Result
- splitn

## Your challenge

Add quoted task titles and return a precise error for an unfinished quote.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
