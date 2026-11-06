"""One-time editorial corrections. Stable lesson IDs, checks and answers remain."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def edit(course, id, rule, replacements=(), addition=""):
 p = ROOT / 'courses' / course / 'lessons' / (id + '.json')
 d = json.loads(p.read_text()); w = d['writing']; w['rule'] = rule
 for old, new in replacements:
  assert old in w['explanation'], (course, id, old)
  w['explanation'] = w['explanation'].replace(old, new)
 if addition: w['explanation'] += "\n\n" + addition
 p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
edit('projects', 'testing', '`#[cfg(test)]` selects test builds, including `cargo test --release`; ordinary builds exclude that module.', [
 ('`#[test]` functions are compiled only for the test harness, so they cost nothing in a release build.', '`#[test]` registers functions with the test harness. A `#[cfg(test)]` module is excluded from ordinary builds, including `cargo build --release`, but included by `cargo test --release`. Test mode and optimization profile are separate choices.')],
 'Compare `cargo test` and `cargo test --release`: both execute assertions. Integer overflow checks normally differ between the default dev and release profiles, and projects can override that policy. Write explicit checked arithmetic when overflow is part of the API contract, rather than relying on the test profile.')
edit('ownership', 'generics', 'Concrete generic instantiations normally use static dispatch; measure code size, allocation and runtime cost.', [
 ('That means generics cost nothing at runtime — but a bound wider than necessary narrows who can call you.', 'This can avoid trait-object dispatch and enable inlining, but it does not make the body, allocations or copies free. Specialization can increase code size and compile time; a bound wider than necessary also narrows who can call you.')])
edit('ownership', 'traits', 'Use generics for static dispatch and trait objects for dynamic dispatch; neither choice alone determines performance.', [
 ('A generic bound is resolved at compile time, so the call is direct and inlinable.', 'A concrete generic instantiation normally selects the implementation statically and may allow inlining.'),
 ('which costs an indirection but lets you store different concrete types together in one collection.', 'which permits heterogeneous values behind pointers. The actual cost depends on the workload and optimizer; dynamic dispatch does not itself require a heap allocation.')])
edit('ownership', 'copy-clone', '`Copy` permits implicit bitwise duplication; `Clone` is explicit and has a type-specific cost.', [
 ('Types that are cheap and have no destructor can be Copy,', 'Types whose fields are all `Copy` and which do not implement `Drop` can implement `Copy`,'),
 ('Everything that owns a heap allocation is not Copy, and duplicating it means calling `.clone()` explicitly', 'An owning `String` or `Vec` is not `Copy`; duplicating those owners requires an explicit operation such as `.clone()`')],
 '`Copy` is a semantic contract, not a promise that the value is small or cheap: a large array of Copy elements is still Copy. `Clone` need not deep-copy data; cloning an `Arc<T>` shares the same allocation and increments its reference count. Decide whether the API needs another owner or independent data.')
edit('ownership', 'drop-order', 'At scope end, remaining locals drop in reverse declaration order; struct fields drop in declaration order.', [
 ('values in a scope drop in reverse declaration order.', 'remaining local bindings in a scope drop in reverse declaration order.')])
edit('ownership', 'closures', 'Call traits depend on how the body uses captures: `Fn` borrows, `FnMut` may mutate, and moving a capture out can require `FnOnce`.', [
 ('`move` forces capture by value, which is what makes a closure safe to send to another thread — the ownership question is answered at compile time rather than by a convention.', '`move` forces capture by value, but sending a closure to another thread also requires `Send` and suitable lifetimes. Moving a reference does not extend the referent’s lifetime, and moving an `Rc` does not make it `Send`.'),
 ('the closure must own data it will use after the creating stack frame is gone, and the relevant types must meet any thread-safety bounds.', 'unscoped `thread::spawn` requires a `Send + \'static` closure. Owned captures are one way to satisfy the lifetime bound; references to static data can also work. Scoped threads may borrow local data because they are joined before the scope exits.')])
edit('ownership', 'associated-types', 'An associated type is fixed per trait implementation; trait parameters can distinguish implementations for the same type.', [
 ('A generic parameter lets a type implement a trait many times; an associated type lets it implement it once with a chosen output.', 'A trait parameter can distinguish multiple implementations for the same implementing type. An associated type is chosen by each particular implementation; a trait may have both parameters and associated types. For a non-generic trait such as `Iterator`, one implementation fixes that type’s `Item`.')])
edit('concurrency', 'concurrency', '`thread::spawn` requires a `Send + \'static` closure; `move` captures by value and does not extend borrowed lifetimes.', [
 ('`thread::spawn` takes a closure that must own everything it touches, which is why `move` appears so often.', '`thread::spawn` requires a `Send + \'static` closure. Owning captured data is a common way to satisfy this, which is why `move` appears often. Borrowing static data is also possible; moving a short-lived reference into the closure does not make it static.')])
edit('concurrency', 'channels', 'A receiver iterator finishes after every sender is dropped and all queued messages have been received.', [
 ('The receiver iterates until every sender is dropped, so the loop ends on its own rather than needing a sentinel message.', 'After every sender is dropped, the receiver drains queued messages and then its iterator ends, so no sentinel message is required.')])
edit('concurrency', 'async-patterns', 'Dropping an owned operation future stops polling it; dropping Tokio’s `JoinHandle` detaches its spawned task.', [
 ('Dropping a future cancels it wherever it is suspended, or before it starts, which is a real advantage over threads — but it means anything that must not be interrupted needs to be written with that in mind.', 'Dropping an owned operation future stops polling that operation, but completed external effects remain. A handle to independently spawned work is different: dropping a Tokio `JoinHandle` detaches the task rather than stopping it.'),
 ('Dropping a future is cancellation: code after its last completed `await` point does not run.', 'Dropping the actual operation future prevents its later polls; cleanup of owned values runs, but ordinary code after its suspension point does not.')],
 'Task ownership matters in timeouts: `timeout(limit, operation())` owns the operation, while timing out a spawned task’s owned `JoinHandle` can merely drop the handle and leave the task running. To request cancellation of an async Tokio task, retain the handle, call `abort()`, and await it to observe termination. Cancellation is cooperative and cannot interrupt a poll that never yields; an already running `spawn_blocking` closure cannot be stopped this way. Use a shutdown protocol for work with effects that must finish or roll back explicitly.')
edit('systems', 'ffi', '`repr(C)` follows C layout rules for the target; it is not a recursive layout, ownership or pointer-validity guarantee.', [],
 '`#[repr(C)]` on an outer struct does not change the representation of an inner field’s type. Define C-compatible representations for nested by-value data too. The resulting size, padding and alignment still depend on the target ABI; do not use an in-memory C layout as a portable file or network format. Document allocator pairing, pointer length and validity, nullability, callback lifetime and unwinding separately.')
edit('systems', 'performance', 'Measure representative workloads with the target optimization profile; debug timings do not predict release performance.', [
 ('`Iterator` chains compile to roughly the same code as a hand-written loop, so readability is rarely the cost.', '`Iterator` chains can optimize similarly to hand-written loops, but inspect representative hot paths rather than assuming identical machine code.'),
 ('measure in release — a debug build is not evidence.', 'measure with the profile and target you intend to ship. Debug timings describe that debug build; they are not a reliable prediction of optimized performance.')])
