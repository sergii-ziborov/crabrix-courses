# Dice Lab

Simulate repeatable dice rolls with an LCG.

## What to notice

A seeded linear congruential generator makes repeatable rolls. Trace how the seed changes on every step and how values become die faces. A different seed changes the sequence while keeping it reproducible.

## How it works

The `next` function mutates a seed with wrapping arithmetic. Each generated number is reduced modulo six and used as an index into an array of face counts; the display adds one to that index so faces read 1 through 6. Because the initial seed is fixed, all 120 rolls repeat across runs. Try a different seed, then compare histograms. Modulo reduction can introduce bias, so this is a repeatable simulation exercise rather than a fair or secure dice source.

## Concepts

- arrays
- wrapping
- simulation

## Your challenge

Roll two dice, chart the totals from 2 through 12, and explain why the distribution is not flat.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
