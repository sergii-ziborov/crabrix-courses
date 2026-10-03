# Iterator Pipeline

One lazy chain from raw text to a ranked result.

## What to notice

Raw input passes through a sequence of small iterator adapters to produce a compact request report. Identify which stage filters, which transforms, and where the lazy chain is finally consumed. Moving a stage can change the result.

## How it works

Each log line is split into fields and converted to a `(path, status, milliseconds)` tuple. `filter_map` drops lines with missing or invalid fields, and `collect` materializes the parsed entries. Later iterator passes count successful status codes, sum durations, and select the slowest entry. Follow a 401 line: it contributes to total requests and time, but not to the success count. The source computes a small report, not a ranking of all requests or a streaming monitor.

## Concepts

- `iterators`
- `closures`
- `sorting`

## Try it

Change the filtering rule and compare the ranking before and after the edit.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
