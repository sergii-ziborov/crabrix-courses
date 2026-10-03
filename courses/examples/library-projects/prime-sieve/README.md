# Prime Sieve

Sieve of Eratosthenes over a boolean Vec.

## What to notice

A boolean vector tracks candidates while multiples are marked as composite. Read the outer candidate loop and inner marking loop, then compare the final entries with the printed prime list.

## How it works

A boolean vector records whether each integer from zero through the limit is still a prime candidate. The loop begins at two and marks multiples of each surviving candidate, starting at its square because smaller multiples were handled earlier. A final pass collects entries that remain true. Compare the printed list with a small hand-checked limit, then try a larger one. The example allocates memory proportional to the limit and is a basic sieve rather than a segmented implementation.

## Concepts

- `Vec`
- `loops`
- `algorithms`

## Try it

Increase the upper bound and verify the first and last primes in the output.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
