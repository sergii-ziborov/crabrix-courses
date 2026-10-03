# Event Bus

Dispatch one event to different trait objects.

## What to notice

Several handlers implement one event trait. The dispatcher can call them through trait objects without depending on each concrete handler type. Add another handler and compare the dispatch code before and after.

## How it works

Both `Counter` and `Reporter` implement the same `Handler` trait. A vector of `Box<dyn Handler>` stores them together, and the nested loops pass each event to every handler. The counter mutates its own state, while the reporter branches on `BuildPassed` versus `Diagnostic`. Add a third handler to see that the dispatch loop needs no new type-specific branch. This is a synchronous in-process demonstration; it has no queue, background worker, or network transport.

## Concepts

- trait object
- Vec<Box<_>>
- dispatch

## Your challenge

Let handlers subscribe to selected event kinds and return collected messages instead of printing directly.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
