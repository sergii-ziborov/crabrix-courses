# Unit Converter

Keep formulas in small typed functions.

## What to notice

Each conversion formula lives in a small typed function. Trace one input through its calculation and formatted output. Add a boundary value to check both the arithmetic and the display.

## How it works

Two small functions keep the Celsius-to-Fahrenheit and kilogram-to-pound formulas separate from display formatting. The loop prints four temperature examples, including a negative value and boiling water, then prints one mass conversion. Edit a test value and compare the formatted result with a hand calculation. The functions accept `f64` directly and do not track a unit type at compile time, so a larger converter would need stronger input validation and unit labeling.

## Concepts

- functions
- f64
- formatting

## Your challenge

Add kilometres-to-miles and reject physically impossible Kelvin temperatures with Result.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
