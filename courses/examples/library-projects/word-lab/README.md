# Word Lab

Build a sorted frequency chart with std.

## What to notice

Text is split, counted by exact spelling, and sorted into a word-frequency chart. Follow one word through each stage and try a repeated word with different capitalization.

## How it works

`split_whitespace` produces words from one fixed phrase. A `BTreeMap` counts each exact spelling through `entry(...).or_insert(0)`, then iterates in sorted key order to print one bar per word. Repeated `rust` and `makes` become longer bars. Add `Rust` with a capital letter and notice it gets a separate entry: the example does not lowercase or strip punctuation. To build a more general frequency tool, choose normalization rules before counting and decide how to handle Unicode and punctuation.

## Concepts

- `BTreeMap`
- `ownership`
- `collections`

## Try it

Normalize case before counting words and compare the sorted frequency chart.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
