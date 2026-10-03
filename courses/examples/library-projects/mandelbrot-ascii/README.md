# Mandelbrot in ASCII

Escape-time fractal drawn with characters.

## What to notice

Each terminal character represents one point in the complex plane. The repeated update stops when the point escapes or reaches the limit; the count selects a visible glyph. Change the sampled range to explore another region.

## How it works

`escape` repeatedly updates a complex point until its squared distance exceeds four or the iteration limit is reached. `main` maps each terminal cell to a coordinate in the complex plane, uses the escape count to choose one of eight shade characters, and prints the rows. Darker-looking regions correspond to points that remain bounded longer under this finite test. Change the sampled coordinate range or iteration limit to reveal different detail; each character is computed again on every run.

## Concepts

- `floats`
- `nested loops`
- `math`

## Try it

Zoom into a smaller coordinate range and compare the shape and detail.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
