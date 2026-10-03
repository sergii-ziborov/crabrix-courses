# RPN Calculator

Evaluate typed tokens with a checked stack.

## What to notice

Tokens are evaluated against a value stack: numbers push, operators consume operands and push a result. Follow one expression token by token, then inspect what happens when operands are missing.

## How it works

Reverse Polish notation puts an operator after its operands. The evaluator pushes each number onto a vector stack; an operator pops the right value first, then the left value, computes a result, and pushes it back. `Result` carries missing-operand and bad-token errors instead of panicking for those cases. Trace `9 3 / 2 -` by writing the stack after every token. The sample returns the top value at the end and does not reject extra unused values or special floating-point outcomes.

## Concepts

- Result
- stack
- parsing

## Your challenge

Add division-by-zero protection and require exactly one value to remain after evaluation.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
