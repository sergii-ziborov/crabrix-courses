# Game of Life

Conway's automaton stepped and printed.

## What to notice

Each cell of a grid changes according to its neighbors. Find the neighbor count and the next-generation rule, then watch the starting pattern evolve. Notice how reading one generation is kept separate from producing the next.

## How it works

A fixed 32 by 16 boolean array holds the current generation. `step` creates a second array, counts eight neighbors for each cell, and applies survival or birth rules before swapping the next grid into place. The source starts with a glider and prints four generations. The neighbor arithmetic uses modulo to wrap at edges, although its horizontal negative-offset constant is based on `HEIGHT`; compare left-edge behavior carefully if you extend it. The separate output grid prevents one updated cell from influencing another during the same step.

## Concepts

- `grids`
- `wrapping`
- `simulation`

## Try it

Change the starting grid and observe whether the pattern stabilizes or repeats.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
