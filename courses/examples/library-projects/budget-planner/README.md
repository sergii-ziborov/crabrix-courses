# Budget Planner

List expenses and calculate a monthly total.

## What to notice

Expenses are records rather than loose strings. Follow one expense from its label and amount into the total and the final report. Changing a single item should change the total by exactly that amount.

## How it works

An `Expense` pairs a label with a floating-point amount. The iterator maps each record to its amount and `sum` produces a monthly total; a second loop prints the individual rows with fixed column widths. There are no categories or persistence in this small example. Add an expense and check that exactly one new row appears and the total changes by that amount. For real money, consider integer minor units or a decimal type instead of binary floating point.

## Concepts

- struct
- iterators
- f64

## Your challenge

Add a category field, then print one subtotal per category before the grand total.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
