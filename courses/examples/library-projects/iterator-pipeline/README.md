# Iterator Pipeline

One lazy chain from raw text to a ranked result.

## What to notice

Raw input passes through a sequence of small iterator adapters to produce ranked output. Identify which stage filters, which transforms, and where the lazy chain is finally consumed. Moving a stage can change the result.

## Concepts

- `iterators`
- `closures`
- `sorting`

## Try it

Change the filtering rule and compare the ranking before and after the edit.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
