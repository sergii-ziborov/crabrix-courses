# Ownership practice terms — 6 November 2026

Ownership Mastery 1.0.10 corrects three short Term Train definitions. Clone follows the type’s implementation and need not deep-copy shared ownership. Copy is implicit bitwise duplication, without a cheapness guarantee. FnMut describes calling through &mut self and can mutate owned or borrowed captures. Stable term/topic IDs, lesson material, answer positions, executable starters and existing progress are unchanged.

The migration parity test now selects its immutable migration archive set explicitly. Retained later editorial archives in dist must not be mistaken for migration fixtures or silently approved as parity. The baseline itself and the expected authored constellation change are unchanged.

Validation: all 28 corpus/package tests passed; 8 packages/771 lessons validated; the signed ownership 1.0.10 archive verified against the production public keyring. Public bytes are verified before catalog activation.

References: [Clone](https://doc.rust-lang.org/std/clone/trait.Clone.html), [Copy](https://doc.rust-lang.org/std/marker/trait.Copy.html), [FnMut](https://doc.rust-lang.org/std/ops/trait.FnMut.html).
