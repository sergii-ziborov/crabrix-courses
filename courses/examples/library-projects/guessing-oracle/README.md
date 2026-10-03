# Guessing Oracle

Deterministic binary search plays its own game.

## What to notice

The search interval shrinks after each midpoint guess. Track the lower and upper bounds until the target is found, then test a value at either edge. This is binary search presented as a small game.

## How it works

The secret is fixed at 73, while the active search range begins at 1 through 100. Each loop computes a midpoint, compares it with the secret, and discards the half that cannot contain the answer. The attempt counter shows how quickly the interval shrinks. Replace the secret with either endpoint and trace the updated bounds. The program simulates both sides of the guessing game locally; it does not request a number from the user.

## Concepts

- `Ordering`
- `loops`
- `binary search`

## Try it

Count how many guesses binary search needs for different target values.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
