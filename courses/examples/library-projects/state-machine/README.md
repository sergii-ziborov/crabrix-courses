# Traffic State Machine

Enums that make an invalid transition impossible.

## What to notice

A traffic signal is modeled with enum states and explicit transitions. Follow each state to its allowed successor. Adding a state makes the compiler reveal every match that needs a new case.

## Concepts

- `enums`
- `match`
- `state`

## Try it

Add a pedestrian phase while keeping impossible transitions unrepresentable.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
