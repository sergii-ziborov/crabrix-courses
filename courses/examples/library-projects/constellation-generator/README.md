# Constellation Generator

A repeatable night sky with two views: a compact terminal drawing and a native
64 by 40 pixel canvas. Soft star halos, a faint band of nebula-like haze, and one
short meteor trail add depth without requiring a graphics library or a network.

## What to notice

The same `SEED` produces the same complete output on every run. There is no clock,
operating-system randomness, or hidden dependency. Change one constant, run the
project again, and compare the result. This makes the example useful for learning
generative art, debugging a renderer, and testing deterministic programs.

The bright crosses are small **static halos**, not an animation. The background
is decorative pixel art, not astronomical data. The generator is not suitable for
passwords, tokens, or other security-sensitive randomness.

## How it works

1. `Rng32` stores a 32-bit state. `next()` applies
   `state.wrapping_mul(1_664_525).wrapping_add(1_013_904_223)`. Wrapping is deliberate:
   arithmetic is modulo 2³² and behaves the same in debug and release builds.
2. The terminal view uses its own sequence starting at `SEED`. In a 38 by 12 grid,
   `next() % 29` selects `✦` for zero, `·` for one through three, and a space for
   everything else. A complete border keeps the drawing readable.
3. The canvas starts a separate sequence at the same seed. Integer distances form
   a faint diagonal haze; small seeded offsets dither its edges. Sparse dust
   pixels add depth. `below()` takes upper generator bits before the remainder;
   the lowest bits of a linear congruential generator repeat too quickly for
   useful coordinate choices. Remainder selection still has a small bias: this is
   a teaching renderer, not a statistically uniform sampler.
4. Up to `STAR_COUNT` stars are placed with a minimum Manhattan distance of four
   cells. A bounded attempt loop prevents unlimited retries. Every fifth accepted
   star gets a two-cell halo; every seventh has a warm core. Other stars remain
   small, keeping the image airy.
5. `paint()` clips writes to the canvas and takes the larger palette index at an
   overlap. The palette indices form a deliberate drawing priority: haze, dust,
   halo, star core. This is **index compositing**, not alpha blending or a general
   calculation of physical brightness. Changing the palette can change its visual
   meaning.
6. One short diagonal meteor trail is stamped over the scene. The final indices
   are encoded as hex characters and printed in a `CRABRIX_CANVAS:` JSON record.
   Crabrix validates and displays that 64 by 40 image; a regular terminal prints
   the record as text. Both views are produced by ordinary Rust.

## Concepts

- Deterministic sequences and explicit state in a `struct`
- Wrapping `u32` arithmetic and upper-bit selection
- Nested loops, `Vec`, `String`, and indexed pixel storage
- Bounded retries, clipped writes, and drawing order
- A small palette and a JSON output protocol

## Try it

Run twice without editing anything. The two outputs should be identical. Then
change `SEED` to `0x12345678`: the stars and dust should move, while the dimensions,
palette, and meteor position remain unchanged. The terminal and canvas restart
their sequences separately; their star positions are not a one-to-one mapping.

Try `STAR_COUNT = 24` for a quieter sky. Change the `% 5` halo interval to `% 8`
for fewer large stars. Adjust the darkest palette colors slightly before changing
the bright cores: restrained contrast makes the glow easier to see.

## Your challenge

Make the meteor position depend on the seed while keeping its five-cell trail
inside the canvas. Keep all writes going through `paint()`, and verify that two
runs with the same seed still match. The attempt limit may produce fewer than
`STAR_COUNT` stars at very high densities; the printed count reports what was
actually placed.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
