# Vending State Machine

Encode valid machine transitions with enums.

## What to notice

Actions are interpreted in an explicit machine state. Follow one valid purchase through its transitions, then compare an action that is rejected in the current state.

## Concepts

- enum
- match
- state machine

## Your challenge

Add sold-out inventory and make an invalid purchase preserve both credit and stock.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
