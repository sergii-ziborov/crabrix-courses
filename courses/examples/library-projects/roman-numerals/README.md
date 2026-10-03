# Roman Numerals

Two-way conversion with slices and folds.

## What to notice

A table of symbols and values drives number conversion in both directions. Trace a subtractive form and compare it with an additive one. Round-trip checks make representation mistakes easier to spot.

## How it works

`to_roman` walks a descending table that includes subtractive pairs such as `CM` and `IV`, repeatedly taking the largest value that still fits. `from_roman` scans individual symbols and subtracts one when the next symbol is larger. The sample converts several integers in both directions to expose disagreements. Try an unusual or invalid Roman string: the decoder does not validate canonical spelling, and unknown symbols become zero. The round trip is a useful check for the listed examples, not a complete parser specification.

## Concepts

- `slices`
- `String`
- `fold`

## Try it

Add round-trip checks for more values and decide how invalid input should be handled.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
