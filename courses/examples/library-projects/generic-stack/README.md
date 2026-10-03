# Generic Stack

One data structure, any type, with trait bounds.

## What to notice

A single stack implementation can store different value types. Inspect its generic type parameter, push and pop operations, and the trait bounds used by the examples. An empty pop is represented explicitly.

## How it works

`Stack<T>` owns a `Vec<T>` and exposes push, pop, peek, length, and a small debug display. The same implementation is instantiated once for integers and once for string slices. `pop` returns `Option<T>`, so draining the word stack ends naturally when it becomes empty; `peek` borrows the top without removing it. The implementation block requires `T: Debug` because `describe` prints the top value, although the storage operations themselves do not inherently need that bound.

## Concepts

- `generics`
- `traits`
- `Option`

## Try it

Add a `peek` method that borrows the top item without removing it.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
