# Markdown Outline

Extract headings into an indented document map.

## What to notice

Headings are detected from lines of Markdown and turned into an indented outline. Look at how the heading prefix determines depth, then try a nested heading and compare the resulting indentation.

## How it works

The program walks a fixed Markdown sample line by line. For each line it counts leading `#` characters, skips non-heading text, and formats a heading with indentation based on its depth. A level-three heading therefore appears beneath a level-two heading in the printed outline. Edit the sample to include an empty heading or a line beginning with `#` but no space. This lightweight recognizer illustrates a prefix rule; it is not a complete CommonMark parser.

## Concepts

- lines
- trim
- slices

## Your challenge

Reject heading jumps such as level 1 directly to level 3 and return a useful line number.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
