# Error Pipeline

A custom error type propagated with ?.

## What to notice

Several fallible functions connect through Result and the ? operator. Follow a successful value through the chain, then locate where an early error returns to the caller. The custom error type keeps failures meaningful.

## Concepts

- `Result`
- `From`
- `Display`

## Try it

Add a failure case and trace how its custom error reaches main through `?`.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
