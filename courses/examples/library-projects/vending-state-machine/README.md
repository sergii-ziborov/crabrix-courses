# Vending State Machine

Encode valid machine transitions with enums.

## What to notice

Actions are interpreted in an explicit machine state. Follow one valid purchase through its transitions, then compare an action that is rejected in the current state.

## How it works

`State` distinguishes an idle machine from one holding a credit balance. `Event` distinguishes inserting money, buying at a price, and canceling. `transition` matches a state-event pair: enough credit reduces the balance, cancel returns to Waiting, and unsupported actions leave the current state unchanged. Trace the sample sequence from 50 credits to a purchase and cancellation. Try buying before inserting money or buying above the balance. The example models transitions only; it does not dispense an item or return change.

## Concepts

- enum
- match
- state machine

## Your challenge

Add sold-out inventory and make an invalid purchase preserve both credit and stock.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
