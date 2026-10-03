# Log Analyzer

Filter structured log lines and count levels.

## What to notice

Log lines are parsed, filtered, and counted by level. Trace one line through all three stages and compare it with one that is skipped. This mirrors the structure of a small real-world data analysis task.

## How it works

The example scans a fixed multiline log, takes the first space-separated word of each line as its level, and increments one of three counters. `INFO`, `WARN`, and `ERROR` are recognized; other prefixes are ignored. The final printout reports counts without keeping the message bodies. Add an unfamiliar level and observe that it affects no counter. This is intentionally narrower than a full log parser: there are no timestamps, structured fields, file input, or malformed-line diagnostics.

## Concepts

- lines
- split_once
- match

## Your challenge

Parse the component after the level, then report the component with the most errors.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
