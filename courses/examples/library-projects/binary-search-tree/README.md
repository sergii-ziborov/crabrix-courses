# Binary Search Tree

Box, Option, and recursion building a real tree.

## What to notice

Nodes own optional left and right children. Follow an insertion from the root to an empty child, then compare the in-order traversal and computed depth. Box makes recursive storage possible; Option makes missing children explicit.

## How it works

Each node owns its children through `Option<Box<Node>>`; insertion borrows one branch mutably and recurses until it finds an empty slot. Values smaller than a node go left, while equal or larger values go right. The example then performs an in-order traversal into a vector and computes the maximum depth. It does not implement a separate lookup operation. Try inserting the numbers in sorted order and compare the resulting depth with the mixed-order tree in the source.

## Concepts

- `Box`
- `Option`
- `recursion`

## Try it

Add an in-order traversal and check that inserted values print in sorted order.

The downloaded example stays unchanged when you open it. Crabrix saves
an editable copy in My Projects.
