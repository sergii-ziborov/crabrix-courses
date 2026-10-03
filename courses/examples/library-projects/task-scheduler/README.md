# Task Scheduler

Order jobs and build a deterministic timeline.

## What to notice

Jobs are ordered into a deterministic timeline. Inspect the job fields and the step that chooses each place in the schedule. Change a duration or priority and compare the resulting order.

## How it works

Each `Job` carries a name, numeric priority, and duration. The vector is sorted by `(priority, duration)`, so lower priorities come first and shorter jobs break ties. The loop advances one clock through the sorted list and prints a start and end interval for each job. Change the priority of `docs` or the duration of `tests` to see how later intervals shift. This is a deterministic, non-preemptive ordering example; it does not execute work concurrently or handle deadlines.

## Concepts

- sort_by_key
- struct
- timeline

## Your challenge

Add release times and make the scheduler choose the shortest available job instead of sorting once.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
