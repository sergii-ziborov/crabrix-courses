# Inventory Ledger

Apply typed stock transactions to a BTreeMap.

## What to notice

Stock changes are typed transactions applied to an ordered item map. Trace one addition or removal into the final inventory. The BTreeMap gives a stable printed order while transaction handling controls valid changes.

## Concepts

- enum
- BTreeMap
- entry

## Your challenge

Return an error when a sale would make stock negative and leave the ledger unchanged.

## Proof

Run the starter first, predict the changed output, make one focused
edit, and Run again with the bundled compiler.
