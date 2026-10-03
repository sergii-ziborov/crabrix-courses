# Todo Board

Track work with structs and an explicit state enum.

## What to notice

Tasks are structs whose status is an explicit enum. Follow a task from its initial enum state into the printed board and completion count. This keeps valid work states visible in the type model.

## How it works

Each task stores a title and one of three `State` variants: Todo, Doing, or Done. The program iterates over a fixed task array to print every status, then filters for Done to compute a completion count. Change one task's initial state and see both its printed line and the count update. The data is constructed fresh on each run: there is no editing command, persistent store, or actual state transition in this example. The enum still makes the possible statuses explicit.

## Concepts

- enum
- struct
- filter

## Your challenge

Add a Blocked state and print a separate count for every state without using string status values.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
