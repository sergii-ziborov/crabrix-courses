# Expression Tokenizer

Turn arithmetic text into typed tokens.

## What to notice

Arithmetic input is scanned into typed tokens before any evaluation. Follow the cursor across a multi-digit number, whitespace, and an operator. Unexpected characters reveal where lexical validation belongs.

## How it works

A peekable character iterator lets the scanner inspect the next character before consuming it. Whitespace is skipped; operators and parentheses become dedicated `Token` variants; runs of digits and periods are parsed as one floating-point number. Invalid numbers and unexpected characters return an error. Follow the cursor through `10 / 2.5` and then through `1 + $`. The result is a token sequence only: the project does not evaluate expressions or implement operator precedence.

## Concepts

- `enums`
- `chars`
- `peekable`

## Try it

Add support for one extra token and show how an unexpected character is reported.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
