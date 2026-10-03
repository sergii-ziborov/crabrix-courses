# FizzBuzz by Match

The classic, written the way Rust wants it.

## What to notice

The combined divisibility case must be considered along with the individual cases. Follow each match arm for a number divisible by both factors, one factor, and neither. The branch order makes the rule readable.

## How it works

`classify` matches the pair of remainders from division by three and five. The `(0, 0)` arm handles values divisible by both before the individual cases; the final arm converts an ordinary number to text. `main` runs the classifier over 1 through 20 and aligns the output. Try values 15, 9, 10, and 7 to exercise every arm. The example is about making the cases exhaustive and explicit, not about parsing input or storing results.

## Concepts

- `match`
- `tuples`
- `ranges`

## Try it

Add a rule for multiples of seven and decide which overlapping rule wins.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
