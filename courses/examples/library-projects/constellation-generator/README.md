# Constellation Generator

Deterministic generative art with no network.

## What to notice

A local deterministic sequence places bright and dim stars. The same seed produces the same sky, which makes small visual changes easy to compare. Trace the number sequence into each cell and the final drawing step.

## How it works

A fixed seed feeds a wrapping multiply-and-add step for each cell in the 38 by 12 terminal grid. The remainder modulo 29 decides whether the cell holds a bright star, a dim mark, or a space. The same seed gives the same sky on every run, which makes visual comparisons repeatable. Change the seed or density thresholds and watch the distribution change. This is a tiny deterministic generator, not an astronomical model or a cryptographically secure random source.

## Concepts

- `algorithms`
- `String`
- `loops`

## Try it

Change the seed or star frequency and compare the two night skies.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
