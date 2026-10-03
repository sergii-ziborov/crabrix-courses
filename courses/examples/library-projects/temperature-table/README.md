# Temperature Table

Formatting, floats, and a tidy aligned table.

## What to notice

Small conversion formulas feed a neatly aligned table. Follow one number through the calculation and its formatting width. Negative or larger values are useful checks for the display.

## How it works

The loop generates Celsius values from minus twenty to thirty in steps of five. `to_fahrenheit` applies the conversion formula, while Kelvin is printed by adding 273.15. Width and precision specifiers keep positive and negative rows aligned in three columns. Follow one row through both formulas, then change the start or step. The example demonstrates formatting a calculated report; it does not read a sensor or validate an arbitrary temperature input.

## Concepts

- `floats`
- `formatting`
- `iterators`

## Try it

Add a Kelvin column and keep every numeric column aligned.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
