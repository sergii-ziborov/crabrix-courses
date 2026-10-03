# Ferris Pixel Art

Render a crab from strings and iterators.

## What to notice

Ferris is stored as six rows of text, not as a bitmap. Spaces and backslashes are part of the drawing: their positions determine the shape in Output. Read the array first, then the iterator that prints one row per line.

## How it works

The `ferris` array holds the art as six raw string literals. Raw strings keep the backslashes readable; each element is one output row. `iter().for_each` prints those rows in order with `println!`, while the header and closing line are printed separately. Try editing one row and run again: a single extra space can shift that part of the crab.

## Concepts

- `arrays`
- `iterators`
- `stdout`

## Try it

Change one row of the crab art, then add a second expression without breaking its alignment.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
