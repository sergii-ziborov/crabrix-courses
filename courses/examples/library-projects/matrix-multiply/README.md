# Matrix Multiply

Nested Vec maths with a printed result grid.

## What to notice

Every output cell combines one row of the first matrix with one column of the second. Trace the row, column, and accumulation loops. Change one input entry and predict which output cells should change.

## How it works

The output matrix starts with one cell for every left-hand row and right-hand column. Three nested loops choose an output cell, multiply matching positions from its row and column, and accumulate the products. Change a single entry in the left matrix to predict which output row changes. The source assumes rectangular, compatible, nonempty inputs and indexes directly into them; it does not perform shape validation. That makes the core calculation easy to inspect but unsuitable as a general matrix API.

## Concepts

- `Vec<Vec<T>>`
- `indexing`
- `math`

## Try it

Add a dimension check so incompatible input matrices return a useful error.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
