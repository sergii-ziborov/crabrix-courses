#!/usr/bin/env python3
"""Apply the audited Rust corrections while retaining lesson and answer IDs."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/'courses'
CHANGED=[]
def edit(course,id,**fields):
    path=ROOT/course/'lessons'/f'{id}.json';lesson=json.loads(path.read_text());w=lesson['writing'];w.update(fields)
    depth=lesson['depth'];depth['correction']=w['rule']
    wrong=next(a for i,a in enumerate(w['answers']) if i!=w['correctAnswer'])
    depth['misconception']='“'+wrong+'”'
    path.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n');CHANGED.append((course,id))

edit('concurrency','pinning-intuition',
 exampleCode='''use std::pin::Pin;
fn main() {
    let mut text = String::from("crab");
    let pinned = Pin::new(&mut text);
    let moved = std::mem::take(Pin::into_inner(pinned));
    assert_eq!(moved, "crab");
    assert!(text.is_empty());
    println!("Unpin permits the move: {moved}");
}''',
 practiceCode='''use std::pin::Pin;
fn main() {
    let mut text = String::from("crab");
    let pinned = Pin::new(&mut text);
    let moved = std::mem::take(Pin::into_inner(pinned));
    println!("{moved}");
}''',
 rule='`Pin` constrains moves of a pointee that relies on pinning. `Unpin` types such as `String` opt out of that restriction; moving the pointer wrapper itself is a separate matter.',
 exampleCaption='This complete safe program moves a String out through Pin because String implements Unpin. It contrasts with a location-sensitive !Unpin pointee.',
 question='Why is moving the String out through Pin safe in this example?',
 answers=['String implements Unpin, so this pinning wrapper does not forbid the move','Pin makes String thread safe','Pin gives the borrowed String a static lifetime'],
 feedback='Unpin opts a type out of pinning movement restrictions. The guarantee for an address-sensitive !Unpin pointee does not apply to this String.',
 task='Run the safe String example, then explain why the same safe extraction API is unavailable for an address-sensitive !Unpin pointee. Do not use unsafe code to bypass its contract.')

edit('projects','errors',
 exampleCaption='The ? operator returns an Err to the caller, which can handle or propagate it.',
 question='What does unwrap() do if this file operation returns Err?',
 answers=['Returns an empty string on failure','Panics; unwinding or process abort depends on the panic configuration','Logs a warning and continues with a default'],
 feedback='unwrap panics on Err. With unwinding, an appropriate boundary may catch that panic; panic=abort terminates the process. Return Result for expected I/O failures rather than using panic as routine control flow.')

edit('systems','cfg-features',
 rule='`#[cfg(...)]` excludes selected code before name and type checking, but source syntax still has to parse. Disabling default features on one dependency edge does not prohibit another edge from enabling them.',
 exampleCode='''#[cfg(target_os = "wasi")]
fn platform() -> &'static str { "wasi" }
#[cfg(not(target_os = "wasi"))]
fn platform() -> &'static str { "native" }

#[cfg(feature = "extras")]
fn extra() -> u32 { 7 }

fn main() {
    println!("{}", platform());
    #[cfg(feature = "extras")]
    println!("{}", extra());
}''',
 question='What does default-features = false request on this dependency declaration?',
 answers=['Disable the dependency completely','Do not request its default feature set on this edge; other dependency edges can still enable it','Prohibit every feature throughout the entire dependency graph'],
 feedback='Feature requests are unified for a package where Cargo resolves them together. This declaration omits defaults; it is not a graph-wide prohibition of std or of another named feature.',
 exampleCaption='Matching cfg predicates select the platform implementation; enabling extras adds a second print. Every branch retains valid Rust syntax.')

edit('concurrency','async-cancellation',
 exampleCode='''use std::{cell::Cell, future::Future, task::{Context, Poll, Waker}};
fn main() {
    let saved = Cell::new(false);
    let acknowledged = Cell::new(false);
    let mut operation = Box::pin(async {
        saved.set(true);
        std::future::pending::<()>().await;
        acknowledged.set(true);
    });
    let mut cx = Context::from_waker(Waker::noop());
    assert!(matches!(operation.as_mut().poll(&mut cx), Poll::Pending));
    drop(operation);
    assert!(saved.get());
    assert!(!acknowledged.get());
    println!("saved={} acknowledged={}", saved.get(), acknowledged.get());
}''',
 question='What cancels an ordinary owned future, including one that has not been polled?',
 answers=['Dropping that future; its body may not have started or may have suspended','Only reaching the end of the async body','Dropping any runtime join handle always cancels its task'],
 feedback='A future can be dropped before its first poll or between polls. Dropping a task handle has separate runtime-specific semantics and may detach its task. Cancellation does not undo effects already performed.',
 exampleCaption='One explicit poll saves state and then suspends. Dropping the future cancels the remaining acknowledgement, while saved=true remains observable.',
 task='Run the complete example and predict saved=true acknowledged=false. Then move drop before the first poll and predict that neither effect occurs. Relate this local demonstration to idempotent external operations.')

edit('interview','q-indexes',
 rule='Leading columns often make a composite B-tree scan selective, but later-column predicates can still use an index, including through skip scan. The actual choice depends on the database, statistics and query plan.',
 exampleCode='''-- PostgreSQL SQL; the events table already exists.
CREATE INDEX events_tenant_kind_at ON events (tenant_id, kind, at);
EXPLAIN SELECT tenant_id, kind, at
FROM events
WHERE kind = 'click' AND at > TIMESTAMP '2026-10-01';''',
 exampleCaption='Inspect EXPLAIN with representative data. An absent leading-column filter does not universally prohibit an index scan.',
 question='Can the index (tenant_id, kind, at) be ruled out solely because tenant_id is not filtered?',
 answers=['Yes, every database forbids using a non-leading index column','No; index and skip-scan choices depend on the database and data, so inspect EXPLAIN','The column names alone guarantee that the index will be chosen'],
 feedback='PostgreSQL documents multicolumn B-tree skip scans and later-column restrictions. A leading predicate is often useful, but index eligibility and planner choice are different questions.',
 task='Use EXPLAIN on both a leading-column query and a later-column query in the named database. Compare selectivity, data distribution and actual plans instead of predicting a universal yes or no.')

edit('interview','q-complexity',
 exampleCaption='Linear and logarithmic growth are different complexity classes. Constants and memory locality still affect measured performance at a particular size.',
 task='Compare a linear scan and an ordered-tree lookup for representative input sizes. Explain the different growth rates, then measure constants without claiming a universal crossover size.')

edit('ownership','phantom-data',
 question='What layout is guaranteed for PhantomData<T> itself?',
 answers=['Size zero and alignment one for every T','One pointer, regardless of T','The same size and alignment as T'],
 feedback='PhantomData<T> is guaranteed to have size 0 and alignment 1 for every T. Its ownership, variance and auto-trait effects still matter; the containing structure has its own layout.')

# Remove the obsolete absolute claims where they occur earlier in the reading.
replacements={
 ('systems','cfg-features'):[('cfg removes code before compilation; a disabled branch never has to be valid.','cfg excludes items before name/type checking; its syntax must still parse.'),('`#[cfg(...)]` removes code before type checking, so a platform-specific branch costs nothing on other targets and does not even have to compile there.','`#[cfg(...)]` removes selected code before name and type checking, so platform-specific names need not resolve on other targets. Its source must still have valid Rust syntax.')],
 ('interview','q-indexes'):[('A B-tree index turns a full scan into a logarithmic descent, which is why the leftmost-prefix rule matters: an index on (a, b) helps a query filtering on a, and on a and b, but not one filtering only on b. Every index also has to be maintained on write, so a table with ten indexes is a slow table to insert into.',
 'A selective B-tree index can reduce work by narrowing the scanned range. Leading-column predicates are often especially useful, but they are not a universal eligibility rule: PostgreSQL can use later-column constraints and skip scans when its planner estimates that they are worthwhile. Every maintained index also adds storage and write work; measure those costs rather than declaring a table slow from its index count alone.')],
 ('projects','doc-examples'):[('`Some` fences','Some fences')],
 ('concurrency','pinning-intuition'):[('`Some` future state machines','Some future state machines')],
 ('concurrency','async-cancellation'):[('An `async` operation may be cancelled when its future is dropped, often after it has yielded at an `.await`.','An owned future can be cancelled by dropping it before its first poll, before its body has run, or between polls after it has suspended.')],
 ('ownership','phantom-data'):[('The marker has no runtime payload, but it is not decorative.','PhantomData<T> itself has guaranteed size zero and alignment one for every T. The containing structure still follows its own layout rules. The marker has no runtime payload, but it is not decorative.')],
 ('interview','q-complexity'):[('A linear scan of a contiguous `Vec` often beats a logarithmic tree for small inputs because the constant factor is cache locality. The useful answer names the input size where the asymptotic term takes over, and mentions amortised cost: push on a `Vec` is O(1) amortised, but the reallocation that makes it so is O(n) and happens at the worst moment.','A linear scan of a contiguous Vec can beat a logarithmic tree for small inputs because locality and constant costs matter. These growth classes are different. Measure a named workload to find any observed crossover; there is no universal input size. Distinguish amortised cost too: Vec::push is O(1) amortised, while an individual reallocation can move O(n) elements.'),('These details `let` someone','These details let someone')],
}
for (course,id),pairs in replacements.items():
 path=ROOT/course/'lessons'/f'{id}.json';lesson=json.loads(path.read_text())
 for field,value in lesson['writing'].items():
  if isinstance(value,str):
   for old,new in pairs:value=value.replace(old,new)
   lesson['writing'][field]=value
 path.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n')
 if (course,id) not in CHANGED:CHANGED.append((course,id))

details={
 ('concurrency','pinning-intuition'):{
  'concept':'Distinguish a pinned !Unpin pointee from an Unpin value and its movable pointer wrapper',
  'traceSteps':[
   {'title':'Identify the pointee','detail':'The pointee is a String, which implements Unpin. Its heap allocation and the stack slot holding String are different locations.'},
   {'title':'Follow safe extraction','detail':'Pin::into_inner returns the mutable String reference because String is Unpin. mem::take moves its value and leaves an empty String.'},
   {'title':'Compare a location-sensitive type','detail':'For an address-sensitive !Unpin pointee, safe extraction through this API is unavailable. Moving a Pin<Box<T>> handle still leaves the boxed pointee at its allocation.'}],
  'transferChallenge':'Draw separate boxes for a String, its byte buffer, a Pin<Box<T>> handle and its pointee. Explain which address is constrained for an address-sensitive !Unpin T.',
  'illustration':{'path':'media/pinning-intuition.png','alt':'Three panels distinguish a safely movable Unpin String, a location-sensitive !Unpin self-reference, and a movable Pin<Box<T>> handle whose pointee stays at its heap address. A small crab marks the contract.','caption':'Pin constrains a location-sensitive !Unpin pointee; String opts out through Unpin. Moving the owning pointer wrapper is a separate operation.'}},
 ('interview','q-indexes'):{
  'concept':'Composite index selectivity, planner choices, skip scans and write cost',
  'traceSteps':[
   {'title':'Name the database','detail':'The worked SQL targets PostgreSQL. Index eligibility and cost estimates depend on the engine, version and statistics.'},
   {'title':'Inspect both predicate shapes','detail':'Compare a tenant_id equality with the later-column kind and at filters. Inspect EXPLAIN; PostgreSQL can consider a skip scan without equality on the first column.'},
   {'title':'Measure the tradeoff','detail':'Compare estimated and actual rows on representative data, then account for index storage and maintenance on inserts and updates.'}],
  'transferChallenge':'Compare EXPLAIN plans for leading-column and later-column filters with two different tenant cardinalities. Explain the cost estimate without assuming that an eligible index must be chosen.'},
 ('interview','q-complexity'):{
  'traceSteps':[
   {'title':'Identify the operations','detail':'A linear scan may visit n entries; a balanced ordered tree descends through O(log n) levels.'},
   {'title':'Separate growth from timing','detail':'These are different growth classes. Comparison cost, allocation, cache locality and constants still affect a measured run.'},
   {'title':'Measure a named workload','detail':'Compare representative sizes and key distributions. Report the environment and observations rather than a universal crossover size.'}]},
 ('concurrency','async-cancellation'):{
  'traceSteps':[
   {'title':'Construct without running','detail':'Creating the async block captures references but does not execute saved.set(true). Dropping it now would leave both flags false.'},
   {'title':'Poll until pending','detail':'The explicit first poll sets saved=true and reaches pending().await, returning Poll::Pending before the acknowledgement.'},
   {'title':'Drop the owned future','detail':'Dropping operation cancels the remaining future. The previous saved effect remains true and acknowledged stays false; dropping a runtime task handle has separate semantics.'}]},
}
for (course,id),fields in details.items():
 path=ROOT/course/'lessons'/f'{id}.json';lesson=json.loads(path.read_text())
 for key,value in fields.items():
  if key in ('concept','illustration'):lesson[key]=value
  else:lesson['depth'][key]=value
 path.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n')

Path(__file__).with_name('rust-corrections.json').write_text(json.dumps(CHANGED,indent=2)+'\n')
print('Corrected',len(CHANGED),'Rust lessons')
