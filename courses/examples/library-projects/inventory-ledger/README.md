# Inventory Ledger

Apply typed stock transactions to a BTreeMap.

## What to notice

Stock changes are typed transactions applied to an ordered item map. Trace one addition or removal into the final inventory. The BTreeMap gives a stable printed order while transaction handling makes additions and removals explicit.

## How it works

`Transaction` makes receiving stock and selling stock different cases. `apply` turns either case into a signed change and updates the item's count through `BTreeMap::entry`; iteration over the map prints item names in sorted order. The three sample transactions leave one item reduced and another unchanged after receipt. Try selling more than the available count to see a limitation: this example permits negative stock and does not validate a real purchase. A production ledger would reject that transition and retain an audit trail.

## Concepts

- enum
- BTreeMap
- entry

## Your challenge

Return an error when a sale would make stock negative and leave the ledger unchanged.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
