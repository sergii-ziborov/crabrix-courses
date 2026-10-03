# Run-Length Encoder

Compress and expand a string, round-trip checked.

## What to notice

Consecutive equal characters become a count followed by one character. encode uses a peekable iterator; decode collects ASCII digits as the next count. The sample round-trips, but arbitrary input containing digits needs an escaping rule.

## How it works

`encode` wraps `input.chars()` in `peekable()` so it can see whether the next character extends the current run. It writes the run length and then the character. `decode` gathers digits until a non-digit arrives, repeats that character, and clears the count. `main` verifies the sample with `assert_eq!`. Notice the format has no escape marker for source digits, so it is intentionally limited.

## Concepts

- `chars`
- `String`
- `assert`

## Try it

Try empty input and long runs, then verify decoding restores the original text.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
