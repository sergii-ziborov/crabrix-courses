# RPN Calculator

Evaluate typed tokens with a checked stack.

## What to notice

Tokens are evaluated against a value stack: numbers push, operators consume operands and push a result. Follow one expression token by token, then inspect what happens when operands are missing.

## Concepts

- Result
- stack
- parsing

## Your challenge

Add division-by-zero protection and require exactly one value to remain after evaluation.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
