# ASCII Histogram

Turn numeric data into a terminal chart.

## What to notice

Each input value becomes a row of repeated characters, turning numbers into a chart you can read in a terminal. Follow the loop that pairs a label with its bar and look at the formatting that keeps rows aligned.

## How it works

The `bar` function repeats one block character for the requested value. `main` keeps day labels and counts together as tuples, then formats each label beside its bar. The display is intentionally proportional to raw counts, so a value of twelve occupies three times the width of a value of four. Change a sample to zero and see how the label remains while its bar disappears. This is a terminal chart, so alignment and character width matter as much as the arithmetic.

## Concepts

- arrays
- repeat
- formatting

## Your challenge

Scale values larger than 20 into a fixed-width bar and label the maximum row.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
