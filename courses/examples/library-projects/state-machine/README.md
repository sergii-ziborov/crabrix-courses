# Traffic State Machine

Enums that make an invalid transition impossible.

## What to notice

A traffic signal is modeled with enum states and explicit transitions. Follow each state to its allowed successor. Adding a state makes the compiler reveal every match that needs a new case.

## How it works

`Light` has exactly three states, and `next` defines the transition from each one to its successor. A second method gives every state a duration. Starting at red, `main` prints six states while adding each duration to a clock, then shows the state reached after those transitions. Change a duration to see the timeline move without changing transition order. Adding a new enum case requires deliberate updates to both matches, which is useful when a state must always have a defined successor and timing.

## Concepts

- `enums`
- `match`
- `state`

## Try it

Add a pedestrian phase while keeping impossible transitions unrepresentable.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
