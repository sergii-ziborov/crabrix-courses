# Error Pipeline

A custom error type propagated with ?.

## What to notice

Several fallible functions connect through Result and the ? operator. Follow a successful value through the chain, then locate where an early error returns to the caller. The custom error type keeps failures meaningful.

## How it works

`port` asks `lookup` for a raw value, parses it as `u32`, then checks the allowed port range. The `?` operator returns a `ConfigError` immediately when an earlier step fails; `Display` turns each variant into a useful message. The sample tries a valid number, text, an out-of-range number, and a missing key. The tiny `lookup` implementation examines the first `key=value` line only, so it is not a general configuration-file parser.

## Concepts

- `Result`
- `From`
- `Display`

## Try it

Add a failure case and trace how its custom error reaches main through `?`.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
