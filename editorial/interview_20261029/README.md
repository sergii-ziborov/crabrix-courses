# Interview Prep review — 29 October 2026

Interview 1.1.0 expands 40 existing lessons to **52**, with 12 separate new
questions, worked std examples, explanations, plausible alternatives and oral
follow-ups. Three new units are appended. Existing lesson IDs, unit order and
all 40 correct-answer positions are retained; the baseline manifest records them.

Topics added: interior mutability; Copy/Clone/Cow; UTF-8 and editor coordinates;
iterator ownership/laziness; closure traits; Pin/Unpin; Send across await;
lock scope in futures; native async traits/dyn compatibility; typed error
boundaries; coherence/newtypes; checked integer arithmetic and conversions.

All 40 old prompts, practice blocks, answer sets and feedback were reviewed.
Corrections include: a borrow-conflict example that previously compiled; Arc's
inner Send/Sync bounds; non-guaranteed machine-byte move counts; virtual-memory
cost claims; TCP-level HTTP/2 loss effects; quorum intersection versus a complete
consistency protocol; idempotency keys versus atomic server deduplication;
configurable Cargo profiles; fuzzing without promising the first discovered bug;
and non_exhaustive as a planned contract rather than a universally compatible
retrofit. Contextual SQL, protocol, dependency and declaration blocks are labelled.
Two Sum has a complete deterministic implementation with widened i32 arithmetic.

`verify_examples.py` records **48 actual desktop Rust 2024 checks**: 42 programs
compile and run, and six deliberate errors fail for their expected diagnostic.
Every new worked example executes. The 56 remaining blocks are explicitly
contextual snippets (including SQL, dependencies and API sketches), or the
intentional division-by-zero debugging example. They are not claimed to be 56
successfully executed standalone Rust programs. Source digests accompany checks.
The native production-signature installer, all 52 image decodes, old-session preservation and all twelve new worked examples passed on phone/iPad Simulator. The gate has 39 native checks and one UI flow per device; details are in native-qualification.json. Public delivery is recorded separately.

All lessons retain an exact code-to-rule map or matching existing artwork.
New/changed deterministic maps extend the existing `render_rust` lesson renderer;
Matching existing illustrations were retained where code, rule and caption
remained unchanged; changed contextual captions received updated maps. No app UI template, editor or theme was changed
by the educational-content update. Diagrams do not use invented performance data.

Primary references checked for current API contracts:

- [Rust Pin documentation](https://doc.rust-lang.org/std/pin/)
- [Future::poll](https://doc.rust-lang.org/std/future/trait.Future.html)
- [Tokio spawn bounds](https://docs.rs/tokio/1.54.1/tokio/task/fn.spawn.html)
- [Tokio mutex guidance](https://docs.rs/tokio/1.54.1/tokio/sync/struct.Mutex.html)
- [Dyn compatibility](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility)
- [Coherence and orphan rules](https://doc.rust-lang.org/reference/items/implementations.html#trait-implementation-coherence)
- [RefCell Send/Sync and borrow guards](https://doc.rust-lang.org/std/cell/struct.RefCell.html)
- [Arc thread safety](https://doc.rust-lang.org/std/sync/struct.Arc.html#thread-safety)
- [Vec guarantees](https://doc.rust-lang.org/std/vec/struct.Vec.html#guarantees)
- [Cow](https://doc.rust-lang.org/std/borrow/enum.Cow.html)
- [FnMut](https://doc.rust-lang.org/std/ops/trait.FnMut.html)
- [String boundaries](https://doc.rust-lang.org/std/primitive.str.html#method.get)
- [Iterator adapters](https://doc.rust-lang.org/std/iter/trait.Iterator.html)
- [Checked addition](https://doc.rust-lang.org/std/primitive.u32.html#method.checked_add)
- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/18/transaction-iso.html)

This is a practical learning and interview corpus, not a guarantee that every
employer asks these questions or that any finite question bank covers all jobs.
For a role-specific interview, choose relevant topics and change one constraint
in the follow-up instead of memorizing answer positions.
