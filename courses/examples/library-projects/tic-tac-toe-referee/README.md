# Tic-Tac-Toe Referee

Evaluate a board with indexed winning lines.

## What to notice

The board is checked against indexed winning lines, and reports a winning mark when one exists. Trace a diagonal win and a full board without a winner through the decision path.

## How it works

The board is a nine-character array, and `winner` checks eight predefined triples: three rows, three columns, and two diagonals. A triple only wins when its cells have the same non-space mark. `main` prints the sample board and reports the optional winner. Change a diagonal mark and predict the result before running. This example does not determine whether a board is a draw, enforce alternating turns, or validate how the position was reached; it only detects a winning line.

## Concepts

- arrays
- Option
- patterns

## Your challenge

Detect a draw separately from an unfinished board and validate that turn counts are legal.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
