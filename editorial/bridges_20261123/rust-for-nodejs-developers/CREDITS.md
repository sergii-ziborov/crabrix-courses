# Credits — Rust for Node.js Developers

Finishing a bridge lesson marks these Academy lessons as known in the app.
Each row names the target lesson's rule and the bridge lesson rule and check that cover it.

## console.log vs println! (`node-console-log-to-println`, compiled port challenge)
Bridge rule: Execution starts in `fn main()`; `println!` and `format!` are macros whose placeholders are checked during compilation.
Check: When does rustc report that `println!("{} costs {} cents", item)` is missing an argument?
- `basics/hello-rust` — Hello, Rust: Execution begins in `fn main()`. `println!` is a compile-time-checked macro that writes a formatted line to stdout when the program runs.
- `basics/print-formatting` — Printing Values: Every formatting placeholder must have a value known to `println!`.

## const and let vs let and let mut (`node-let-const-to-let-mut`, quick check)
Bridge rule: `let` is immutable, `let mut` permits change, and a new `let` with the same name shadows the old binding.
Check: Which statement about `let tags = Vec::new(); tags.push("rust");` is true?
- `basics/variables` — Variables: `mut` permits mutation; shadowing hides the old binding behind a new one.

## Number vs Rust integer types (`node-number-to-integer-types`, compiled port challenge)
Bridge rule: Numeric types never mix implicitly: convert with `From` or `try_from`, and choose checked, wrapping or saturating arithmetic where overflow is possible.
Check: `fn left(capacity: u32, booked: u32) -> u32 { capacity - booked }` is called with `3` and `5` in a debug build. What happens?
- `basics/number-types` — Numbers: Numeric conversions are explicit because ranges and precision differ.
- `basics/operators` — Operators & Casting: Numeric operands need compatible types; choose the overflow policy explicitly.

## JavaScript functions vs fn (`node-functions-to-fn`, compiled port challenge)
Bridge rule: Every parameter has a type, arguments must match it exactly, and a block's final expression without a semicolon is its value.
Check: Why is `fn double(x: i32) -> i32 { x * 2; }` rejected?
- `basics/functions` — Functions: The last expression without a semicolon is the return value.
- `basics/function-parameters` — Parameters: Parameters need explicit types; arguments must satisfy them.
- `basics/block-expressions` — Block Expressions: No semicolon means a tail value; a semicolon turns it into `()`.

## Truthiness vs bool, if and match (`node-truthiness-to-bool-and-match`, compiled port challenge)
Bridge rule: `if` requires a `bool`, and every branch of an `if` or `match` expression must produce the same type.
Check: Why does `let label = if count > 0 { count } else { "none" };` not compile?
- `basics/booleans-comparisons` — Booleans: `if` requires `bool`; Rust has no implicit numeric truthiness.
- `basics/control-flow` — Control Flow: `if` is an expression; every branch must produce the same type.

## Classes and objects vs structs (`node-objects-to-structs`, compiled port challenge)
Bridge rule: `&self` reads, `&mut self` modifies and `self` consumes: the receiver tells the caller what a method does to the value.
Check: What does `fn finish(self) -> u32` tell a caller that `fn count(&self) -> u32` does not?
- `basics/structs` — Structs: `self` consumes, `&self` reads, `&mut self` modifies.
- `basics/methods-intro` — Using Methods: Read a method's `self` parameter to learn its ownership effect.

## TypeScript unions vs enums (`node-ts-unions-to-enums`, compiled port challenge)
Bridge rule: An enum variant carries its own data, and `match` must cover every variant; a guard narrows an arm but never excuses a missing case.
Check: A `match` on `Payment` ends with `_ => 0`. Later someone adds `Payment::Crypto`. What happens?
- `basics/enums` — Enums & Match: `match` is exhaustive: every variant must be handled.
- `basics/pattern-matching` — Pattern Matching: A guard narrows an arm; the compiler still demands the set be exhaustive.

## null, undefined and ?? vs Option (`node-null-undefined-to-option`, compiled port challenge)
Bridge rule: Use `Option<T>` when a value may be absent and `Result<T, E>` when the caller needs the reason; `unwrap_or` replaces `??`, not `||`.
Check: A lookup finds nothing when the key is missing, and fails when the storage is unreachable. Which return type gives the caller both facts?
- `basics/option-result` — Option & Result: `Option` for absence, `Result` when the caller needs the reason.

## Array methods vs iterators (`node-array-methods-to-iterators`, compiled port challenge)
Bridge rule: Iterator adapters are lazy: a consumer such as `sum`, `find`, `collect` or a `for` loop drives the work, one item at a time.
Check: In the practice code, what has `map` done by the time `done` prints?
- `ownership/iterators` — Iterators: Adapters are lazy; a consumer is what makes the work happen.
- `ownership/iterator-adapters` — Iterator Pipelines: Adapters such as map and filter describe work but do nothing until a consumer asks for values.

## Objects and Map vs HashMap (`node-map-and-objects-to-hashmap`, compiled port challenge)
Bridge rule: `entry(key).or_insert(default)` looks the key up once and returns a mutable reference to the value, whether or not it was already there.
Check: Why is `*counts.entry(word).or_insert(0) += 1` preferred over `get` followed by `insert`?
- `basics/collections` — Collections: `entry().or_insert()` gives you a mutable reference either way.

## UTF-16 strings vs UTF-8 String (`node-utf16-strings-to-utf8`, compiled port challenge)
Bridge rule: `len()` counts UTF-8 bytes and `chars().count()` counts Unicode scalar values; neither counts graphemes, and a `String` cannot be indexed by position.
Check: What does `"café".len()` return in Rust, where JavaScript's `"café".length` is `4`?
- `basics/strings` — Strings & UTF-8: `len()` counts UTF-8 bytes; `chars().count()` counts Unicode scalar values, not grapheme clusters.
- `basics/chars-and-text` — Characters & Text: `String` indexing by an arbitrary byte is forbidden because UTF-8 boundaries matter.

## Shared references vs ownership (`node-shared-references-to-ownership`, quick check)
Bridge rule: Each value has one owner: assignment or a by-value parameter moves it, `&T` lends it, and `clone()` makes an independent copy.
Check: In the practice code, what is the smallest change that keeps `name` usable after the call, without cloning?
- `ownership/ownership` — Ownership: One value, one owner; a move ends the previous binding.
- `ownership/move-functions` — Moves Across Functions: A parameter of type `String` takes ownership, while `&str` only borrows text.

## Mutating arguments vs borrowing (`node-mutation-to-borrowing`, compiled port challenge)
Bridge rule: `&T` lends read-only access and `&mut T` lends exclusive write access; neither transfers ownership, and the two never overlap.
Check: Why does rustc reject `queue.push(n + 1)` inside `for n in &queue`?
- `basics/references-intro` — First References: `&T` borrows `T` for read-only use without transferring ownership.
- `ownership/borrowing` — Borrowing: Many shared borrows or one mutable borrow, never both at once.
- `ownership/mutable-borrows` — Mutable Borrows: An `&mut` reference permits mutation without transferring ownership.

## TypeScript interfaces vs traits (`node-interfaces-to-traits`, compiled port challenge)
Bridge rule: A type implements a trait only through an explicit `impl`; use a generic bound for static dispatch over one type and `dyn Trait` for a collection of mixed types.
Check: Which signature lets one call handle a list that mixes `Book` and `Coffee` values?
- `ownership/traits` — Traits: Use generics for static dispatch and trait objects for dynamic dispatch; neither choice alone determines performance.

## try/catch vs Result (`node-try-catch-to-result`, compiled port challenge)
Bridge rule: Return `Result` for a failure the caller can act on, propagate it with `?`, and keep panics such as `unwrap` for bugs and broken invariants.
Check: In the practice code, what does `unwrap()` do when `parse` returns `Err`?
- `basics/recoverable-errors` — Handling Failure: Use `Result` for failure the caller can reasonably respond to.
- `projects/errors` — Error Design: Panic for a bug; `Result` for a situation the caller can act on.

## npm and package.json vs Cargo (`node-npm-to-cargo`, quick check)
Bridge rule: In `Cargo.toml` a bare version such as `"1.3.0"` is a caret requirement, `>=1.3.0, <2.0.0`; pin exactly with `"=1.3.0"`, and let `Cargo.lock` record what was resolved.
Check: In `package.json`, a bare `"1.3.0"` pins exactly that version. What does `left-pad = "1.3.0"` mean in `Cargo.toml`?
- `projects/dependencies` — Dependencies: "1.2" means >=1.2.0 and <2.0.0; the lockfile records what was actually chosen.

## Promises vs futures (`node-promises-to-futures`, quick check)
Bridge rule: Futures are lazy: calling an `async fn` only creates a future, and no code inside it runs until something polls it.
Check: What does the practice program print?
- `concurrency/futures` — Futures: Futures are lazy: no poll, no progress.
