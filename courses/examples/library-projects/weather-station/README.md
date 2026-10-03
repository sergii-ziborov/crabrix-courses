# Weather Station

Summarize sensor samples without losing units.

## What to notice

Sensor samples are summarized without losing their unit context. Follow one reading into the aggregate and final report. Adding an outlier reveals which summary values change.

## How it works

`Sample` keeps Celsius temperature and percent humidity together. The iterator sums temperatures and divides by sample count to print an average, while `min_by_key` selects the reading with the lowest humidity. Add a hot but humid sample and see how the average changes without necessarily changing the driest result. The fixed array is nonempty, which makes the final `unwrap` safe here; a general weather service would handle empty input and timestamped readings.

## Concepts

- newtype
- fold
- statistics

## Your challenge

Represent Celsius as a newtype and reject an empty sample slice with Result.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
