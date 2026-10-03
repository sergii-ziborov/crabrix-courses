# Caesar Cipher

Transform ASCII text one character at a time.

## What to notice

This example shifts letters through a fixed alphabet and leaves other characters to an explicit branch. Trace one character through classification, shift, and output. Compare the result with the input before changing the shift distance.

## How it works

`shift` only transforms ASCII lowercase letters. It converts a letter to a zero-based offset from `a`, adds the shift, and uses modulo 26 to wrap after `z`. `encode` maps this function over the input characters and collects a new `String`; punctuation and uppercase letters pass through unchanged. Try shifting `z` by one and a mixed-case sentence by two. The example illustrates a reversible substitution, not secure encryption.

## Concepts

- char
- map
- modulo

## Your challenge

Support uppercase letters and write a decode function that restores the original message.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
