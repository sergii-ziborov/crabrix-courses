# Maze Pathfinder

Find a shortest grid path with breadth-first search.

## What to notice

A VecDeque visits open maze cells in breadth-first order. The first visit records the shortest distance from the start using four orthogonal moves. This example reports the goal distance; it does not reconstruct or draw the path.

## How it works

`VecDeque` stores cells waiting to be visited. The loop tries down, up, right, and left, skipping walls and cells whose distance is already known. Every queued cell gets a distance one larger than its parent. Because the queue visits all cells at a given distance before more distant cells, the first distance written for the goal is minimal. The implementation reports the distance only.

## Concepts

- VecDeque
- grid
- BFS

## Your challenge

Store each cell's predecessor and print the actual shortest route over the maze.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
