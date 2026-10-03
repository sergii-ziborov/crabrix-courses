# CSV Report

Parse embedded rows into structs and summarise.

## What to notice

Comma-separated rows become typed records before they are summarized. Inspect the split and conversion steps, then follow one field into the printed report. Try an incomplete row to see the parser boundary.

## How it works

Each line is split at commas and converted into a `Sale` containing region, product, units, and unit price. `filter_map(parse)` drops rows the parser cannot convert, then `Sale::total` multiplies units by unit price. A sorted, deduplicated list of regions drives the final per-region sums. This intentionally simple parser does not handle quoted commas, escaped fields, or detailed error reporting. Add one malformed row and compare the parsed-row count with the number of input lines.

## Concepts

- `structs`
- `parsing`
- `Result`

## Try it

Add one malformed row and make the parser report its line number without losing the valid rows.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
