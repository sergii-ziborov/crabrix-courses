# Orbit Dashboard

A terminal UI built from a local module.

## What to notice

A local Rust module supplies values that the main file formats as a terminal dashboard. Open both files and trace one value from its source into the displayed line. The split shows how data and presentation can stay separate.

## How it works

`main.rs` declares `mod ui`, so Rust loads the sibling `ui.rs` module at compile time. The module's `bar` function converts a percentage to a ten-cell display using filled and empty characters; `main` supplies the fuel, signal, and oxygen values and prints a framed dashboard. Open both files to see the public function boundary. Try a percentage that is not a multiple of ten and notice the bar truncates to whole cells while the numeric value remains exact.

## Concepts

- `modules`
- `formatting`
- `functions`

## Try it

Add a new metric in the local module and give it a matching dashboard row.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
