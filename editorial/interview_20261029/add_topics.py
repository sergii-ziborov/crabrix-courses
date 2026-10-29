import json,textwrap
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'courses/interview'
new=[]
def add(id,title,concept,unit,order,summary,explanation,example,caption,rule,question,practice,answers,correct,feedback,followup):
 example=textwrap.dedent(example).strip();practice=textwrap.dedent(practice).strip()
 r=dict(id=id,title=title,concept=concept,minutes=14,order=order,parentID=unit,exerciseKind='planned',contentDigest='',writing=dict(summary=summary,explanation=explanation.strip(),exampleCode=example,exampleCaption=caption,rule=rule,task='Explain the example, predict the result, and justify your answer to the follow-up.',practiceCode=practice,success='Identify the relevant ownership or API contract and test the changed constraint.',question=question,answers=answers,correctAnswer=correct,feedback=feedback),depth=dict(misconception=answers[(correct+1)%3],correction=feedback,traceSteps=[dict(title='Observe the concrete input',detail=caption),dict(title='Apply the contract',detail=rule),dict(title='Check the boundary',detail=followup)],transferChallenge=followup,connections=[]))
 p=ROOT/'lessons'/f'{id}.json';assert not p.exists();p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');(ROOT/'checks'/f'{id}.json').write_text(json.dumps({'evidence':{'kind':'reasoning','correctAnswer':correct}},indent=2)+'\n');new.append(id)
add('q-interior-mutability','Cell, RefCell and Runtime Borrows','Interior mutability without confusing Send and Sync','interview-values',0,
'Interior mutability changes how access is checked; it does not remove the safety contract.',
'''Cell<T> is useful when a value can be read or replaced through a shared reference without handing out a reference to its contents. RefCell<T> instead hands out guarded borrows and checks their exclusivity at runtime. borrow_mut can panic on a conflict; try_borrow_mut lets you handle that conflict as an error. The example retains a reader, observes a rejected writer, then drops the reader and mutates successfully.

Neither type automatically supplies synchronized shared access between threads. RefCell<T> can be Send when T is Send, but it is not Sync: transferring a uniquely owned cell is different from sharing references to it concurrently. Arc<RefCell<T>> therefore does not become a thread-safe mutable container simply because Arc has an atomic reference count.

Choose the smallest access contract your data flow needs. An exclusive &mut T is often sufficient. Runtime checking can support single-threaded shared ownership, while a mutex or a message protocol can coordinate cross-thread mutation. In an interview, explain the precise conflict, its error behaviour and how long each guard lives. A lexical scope or explicit drop can release a borrow before another operation; an extra Rc clone does not release a guard.''',
'''use std::cell::RefCell;
fn main() {
    let value = RefCell::new(7);
    let reader = value.borrow();
    assert!(value.try_borrow_mut().is_err());
    assert_eq!(*reader, 7);
    drop(reader);
    *value.borrow_mut() = 9;
    assert_eq!(*value.borrow(), 9);
}''','The writer conflicts only while the shared borrow guard remains live.',
'Runtime borrow checking still enforces exclusivity; ownership transfer and concurrent sharing have different trait bounds.',
'Why does try_borrow_mut return an error while reader is still retained?',
'''use std::cell::RefCell;
fn main() {
    let value = RefCell::new(7);
    let reader = value.borrow();
    let result = value.try_borrow_mut();
    assert!(result.is_err());
    println!("{}", *reader);
}''',
['RefCell forbids every mutation after construction.','A live shared guard prevents an overlapping mutable borrow.','Cloning the outer Rc would automatically end the shared borrow.'],1,
'The guard controls the runtime borrow lifetime. RefCell is not Sync, although an owned RefCell<T> can be Send when T is Send.',
'Why can moving an owned RefCell<String> to one worker be allowed while sharing Arc<RefCell<String>> is not?')
add('q-copy-clone-cow','Copy, Clone and Cow','Implicit duplication, explicit cloning and lazy ownership','interview-values',1,
'Ask which bytes are shared, copied or allocated before choosing an ownership conversion.',
'''Copy permits implicit duplication of a value. Clone is an explicit operation whose cost and semantics depend on its implementation. Cloning an Rc or Arc normally creates another owner of the same allocation; cloning a String normally creates owned string storage. The word clone alone does not tell you which one happened.

Cow stores either borrowed or owned data behind one interface. A borrowed Cow<str> can read a caller’s string without making an owned String. Requesting mutable access through to_mut converts the borrowed form into owned storage when needed. The original borrowed string is not changed. If the Cow already owns a String, obtaining mutable access need not clone that String again.

The example starts with borrowed text, requests a modification and checks that the original remains unchanged. This is a useful API when many inputs pass through untouched and some need normalization. It is not a guarantee that every Cow-based design is faster: consider how often ownership is required and how long the borrowed source must live. State the input lifetime and resulting ownership clearly rather than advertising zero copies for every path.''',
'''use std::borrow::Cow;
fn main() {
    let source = String::from("crab");
    let mut label: Cow<'_, str> = Cow::Borrowed(source.as_str());
    assert!(matches!(label, Cow::Borrowed(_)));
    label.to_mut().push('!');
    assert!(matches!(label, Cow::Owned(_)));
    assert_eq!(source, "crab");
    assert_eq!(label, "crab!");
}''','Mutation converts this borrowed Cow into independent owned text.',
'Clone semantics depend on the type; Cow delays ownership conversion until an operation needs it.',
'What changes when to_mut is called on this borrowed Cow<str>?',
'''use std::borrow::Cow;
fn main() {
    let source = "crab";
    let mut text: Cow<'_, str> = Cow::Borrowed(source);
    text.to_mut().push('!');
    assert_eq!(source, "crab");
    assert_eq!(text, "crab!");
}''',
['It mutates the original borrowed str in place.','It keeps a mutable reference into the original immutable str.','It obtains owned storage and mutates that owned value.'],2,
'The borrowed branch becomes owned before mutation. Cow does not bypass str’s immutability or the lifetime of a borrowed source.',
'Compare cloning String, Arc<String> and Cow<str>. Which operations duplicate text, and which can merely add an owner?')
add('q-utf8-boundaries','UTF-8 and Editor Offsets','Bytes, Unicode scalars, graphemes and UTF-16 positions','interview-values',2,
'Text positions need a declared coordinate system before they can be exchanged or sliced.',
'''Rust str is valid UTF-8. len counts bytes, and chars iterates Unicode scalar values. Neither operation counts user-perceived grapheme clusters in general. A decomposed accent can consist of two scalar values while users perceive one letter. Emoji can occupy several UTF-8 bytes and two UTF-16 code units even before considering combined sequences.

String slicing uses byte offsets and requires valid UTF-8 boundaries. get returns None for an invalid range instead of panicking through indexing. char_indices supplies byte offsets at scalar boundaries; those positions are still not necessarily grapheme boundaries. The example uses a two-byte accented letter and checks both the valid whole-letter range and an invalid split.

An editor or collaboration protocol may exchange UTF-16 offsets. Convert explicitly between that coordinate system and Rust byte positions, and bind the coordinates to the same source revision. A valid offset in an earlier revision can point at a different expression after an edit. For a live interview, ask the candidate to trace one accented string and one emoji through the chosen coordinate system. Testing only ASCII conceals these boundary and synchronization errors.''',
'''fn main() {
    let text = "é🦀";
    assert_eq!(text.len(), 6);
    assert_eq!(text.chars().count(), 2);
    assert_eq!(text.encode_utf16().count(), 3);
    assert_eq!(text.get(0..2), Some("é"));
    assert_eq!(text.get(1..2), None);
    assert_eq!("e\\u{301}".chars().count(), 2);
}''','The same two scalar values occupy six UTF-8 bytes and three UTF-16 units.',
'Validate the coordinate system, source revision and UTF-8 boundaries before slicing text.',
'Why does get(1..2) return None for the two-byte string é?',
'''fn main() {
    let text = "é";
    assert_eq!(text.len(), 2);
    assert_eq!(text.get(1..2), None);
}''',
['The starting byte offset splits the UTF-8 encoding of the scalar.','Rust rejects every string slice containing a non-ASCII value.','get interprets the range as UTF-16 positions rather than bytes.'],0,
'Byte 1 is a continuation byte, not the start of a scalar. Use checked byte ranges or explicitly convert from the editor’s coordinate system.',
'What does chars().count() return for e plus a combining acute accent, and why is that not a grapheme-counting solution?')
add('q-iterator-ownership','Iterator Ownership and Laziness','Borrowing iteration, consuming iteration and deliberate collection','interview-values',3,
'An iterator pipeline describes work; the item type and terminal operation determine ownership and execution.',
'''For a Vec<T>, iter normally yields &T, iter_mut yields &mut T and into_iter on an owned vector yields T. The chosen receiver matters: into_iter on a reference can still borrow. Read the actual item type before deciding whether an operation moves, copies or clones values.

Most iterator adapters are lazy. map describes a transformation, while a consumer such as collect or sum drives it. Returning an iterator can avoid collecting an intermediate vector, but keeps any captured input borrows alive for the returned iterator’s lifetime. Calling cloned on an iterator of references requests Clone on its items; it is not a free conversion for every T.

The example computes lengths by borrowing the strings and then proves the original vector remains usable. A second pipeline consumes it into another collection. Explain both the data flow and when work occurs. In an interview, follow up by returning an impl Iterator<Item = &str> tied to the input. That exposes lifetime reasoning more clearly than naming adapter methods from memory.''',
'''fn main() {
    let words = vec![String::from("crab"), String::from("rust")];
    let lengths: Vec<_> = words.iter().map(String::len).collect();
    assert_eq!(lengths, [4, 4]);
    assert_eq!(words.len(), 2);
    let owned: Vec<String> = words.into_iter().collect();
    assert_eq!(owned[0], "crab");
}''','Borrowing iteration preserves the input; owned into_iter consumes this vector.',
'Trace the receiver, iterator item type and consumer before making a move or allocation claim.',
'Why can words still be read after collecting these lengths?',
'''fn main() {
    let words = vec![String::from("crab")];
    let lengths: Vec<_> = words.iter().map(String::len).collect();
    assert_eq!(words[0], "crab");
    assert_eq!(lengths, [4]);
}''',
['collect implicitly clones every String in the source vector.','iter yields shared references and the map produces lengths without moving strings.','Every iterator pipeline automatically returns ownership to its original container.'],1,
'The pipeline borrows &String values and collects usize results. A consuming receiver or a different adapter can change the ownership contract.',
'Return an iterator of &str instead of a Vec. Which lifetime connects that iterator to the input, and when is its map closure executed?')
# Later topic definitions are appended before finalization.
add('q-closure-traits','Fn, FnMut and FnOnce','Capture ownership and how a closure uses its environment','interview-async-contracts',0,
'The call trait follows what the closure does with captures, not just whether move appears.',
'''Fn closures can be called through a shared reference, FnMut permits a mutable receiver, and FnOnce consumes its receiver. The traits form a hierarchy: a closure that implements Fn also works where FnMut or FnOnce is required. Every closure supports at least FnOnce, but consuming a captured non-Copy value can make a closure callable only once.

The move keyword determines how captures enter the closure. It does not alone make the closure FnOnce-only. A move closure that merely reads owned data may still implement Fn. Conversely, mutating captured state generally requires FnMut. The example borrows a counter mutably, calls the closure twice, then ends its scope before reading the counter directly.

Read the implementation and the caller’s intended use together. A callback stored for repeated notifications needs a repeated-call contract, while a one-shot cleanup callback can accept FnOnce. If the callback crosses a thread or task boundary, Send and lifetime bounds are additional questions. In an interview, ask the candidate to change only the closure body from reading a String to returning the owned String and explain which call capability is lost.''',
'''fn twice(mut callback: impl FnMut()) {
    callback();
    callback();
}
fn main() {
    let mut count = 0;
    { twice(|| count += 1); }
    assert_eq!(count, 2);
    let text = String::from("crab");
    let read = move || text.len();
    assert_eq!(read(), 4);
    assert_eq!(read(), 4);
}''','A mutating callback runs twice, while a read-only move closure remains repeatedly callable.',
'Move controls capture ownership; the closure body determines its call-trait capabilities.',
'Why can this move closure be called twice?',
'''fn main() {
    let text = String::from("crab");
    let length = move || text.len();
    assert_eq!(length(), 4);
    assert_eq!(length(), 4);
}''',
['move makes every captured String implicitly Copy.','The captured String is recreated before every call.','The body reads the owned capture without consuming it.'],2,
'The closure owns text but only borrows it during each call. Returning text by value instead would consume that capture.',
'Change the body to return text itself. Which trait is then sufficient for the caller, and why is a second call rejected?')
add('q-pin-future','Pin, Unpin and Future Polling','Stable pointees without confusing the pointer with its allocation','interview-async-contracts',1,
'Pin constrains moving a pointee through a pointer; moving that pointer can remain valid.',
'''A future’s poll method receives Pin<&mut Self>. Some futures may have address-sensitive state, so the polling interface must not allow callers to move that state out after pinning. Unpin marks types for which the pinning restriction can be relaxed. Pin is not a mutex and does not itself provide synchronization or permanent storage.

The example pins a compiler-generated async future in a Box, records the pointee’s address, moves the Pin<Box<_>> handle and polls through its pinned mutable reference. Moving the handle does not relocate its heap pointee. A noop waker is adequate only because this particular future completes immediately; it is not a general executor for I/O or pending tasks.

Safe code should use supported pinning constructors and projection APIs instead of inventing unchecked pointer manipulations. A self-referential structure or pinned field needs a careful destruction and projection contract. In an interview, distinguish moving a pointer from moving the pointee, then explain why get_mut requires Unpin. Do not promise that every future is self-referential or that boxing every future is universally necessary.''',
'''use std::future::Future;
use std::task::{Context, Poll, Waker};
fn main() {
    let first = Box::pin(async { 7u32 });
    let address = first.as_ref().get_ref() as *const _;
    let mut second = first;
    assert_eq!(second.as_ref().get_ref() as *const _, address);
    let mut cx = Context::from_waker(Waker::noop());
    assert_eq!(second.as_mut().poll(&mut cx), Poll::Ready(7));
}''','Moving the pinned Box handle retains its pointee’s address and permits pinned polling.',
'Pin protects the pointee’s address-sensitive contract; Unpin governs safe access that can move it.',
'Which operation is demonstrated by moving first into second?',
'''fn main() {
    let first = Box::pin(async { 7u32 });
    let before = first.as_ref().get_ref() as *const _;
    let second = first;
    assert_eq!(second.as_ref().get_ref() as *const _, before);
}''',
['The Pin<Box<_>> handle moves while the pinned allocation stays at its address.','The future becomes Unpin because its Box handle was moved.','Pin copies the future into a new allocation on every assignment.'],0,
'The handle’s move does not move its pointee. The example does not establish Unpin for a compiler-generated async future.',
'Why cannot a generic function obtain &mut T from Pin<&mut T> without an Unpin bound through get_mut?')
add('q-future-send','Send Across await','Task state, static bounds and non-Send locals','interview-async-contracts',2,
'Inspect which values survive a suspension before deciding whether a future satisfies Send.',
'''A suspended async computation stores the state needed for a later poll. If that state contains an Rc or another non-Send value, the future may fail a Send bound. A non-Send temporary can still be used inside a future when it does not survive a suspension. The example places Rc in a lexical scope that ends before await and asks the compiler to verify Send on the resulting future.

Tokio spawn requires a Send + static future and a Send + static output even on a current-thread runtime. A separate local-task API supports a different contract; changing the executor’s thread count does not silently change spawn’s signature. static on an owned task does not mean it must run forever: it means the value contains no shorter-lived borrows that would make this use invalid.

The standard-library example checks a type bound without starting Tokio or a network server. It can therefore isolate a compiler error from runtime setup. For an interview follow-up, retain Rc until after await, observe the compiler rejection and identify the retained state. async move can own captured values, but ownership alone does not make every captured type Send.''',
'''use std::rc::Rc;
fn require_send<T: Send>(_: T) {}
fn main() {
    let future = async {
        { let local = Rc::new(7); assert_eq!(*local, 7); }
        std::future::ready(()).await;
    };
    require_send(future);
}''','Rc is gone before suspension; this compile-time probe requires the future to be Send.',
'Send is determined by the future’s actual retained state; async move does not upgrade non-Send types.',
'Why does this intentionally failing Send check reject the future?',
'''use std::rc::Rc;
fn require_send<T: Send>(_: T) {}
fn main() {
    let future = async {
        let local = Rc::new(7);
        std::future::ready(()).await;
        println!("{local}");
    };
    require_send(future); // deliberate compile error
}''',
['Every async function requires an operating-system thread for its whole lifetime.','Rc remains part of the future’s state across await and is not Send.','The ready future’s unit output is not Send on any runtime.'],1,
'Later use retains Rc across the await in the future’s state. Narrowing its lexical scope before await can remove it from that state.',
'Why does tokio::spawn still require Send on a current-thread runtime, and how does spawn_local deliberately differ?')
add('q-async-locks','Lock Scope Across await','Synchronous blocking, suspension and cancellation-safe critical sections','interview-async-contracts',3,
'Keep synchronous critical sections short and make suspension while holding a guard an explicit design decision.',
'''A standard mutex can be a reasonable choice for a short critical section that does not cross await. Acquiring a contended synchronous mutex can block the executor worker. Holding its guard while a future suspends is a separate problem: it keeps the lock unavailable and can violate a Send bound or participate in a deadlock.

The example updates a counter inside a lexical scope, drops the guard and only then awaits. A compile-time Send check confirms this particular future does not retain the standard MutexGuard across suspension. It does not prove absence of every deadlock or that every acquisition is cheap.

An async mutex can yield while waiting for its lock, but it does not make arbitrary guarded work nonblocking. Avoid awaiting a child task that needs the same lock you hold. For cancellation, define what state is left behind when a task drops after a partial update; lock release is not a business transaction rollback. In an interview, draw lock acquisition, state update, guard drop and each suspension point before arguing about mutex brands.''',
'''use std::sync::Mutex;
fn require_send<T: Send>(_: T) {}
fn main() {
    let value = Mutex::new(0);
    let future = async {
        { let mut guard = value.lock().unwrap(); *guard += 1; }
        std::future::ready(()).await;
    };
    require_send(future);
}''','The synchronous guard’s scope ends before await; the future passes this Send check.',
'Waiting for a lock, holding a lock during suspension and doing CPU work are separate concerns.',
'What change would make this future retain the standard MutexGuard across await?',
'''use std::sync::Mutex;
fn require_send<T: Send>(_: T) {}
fn main() {
    let value = Mutex::new(0);
    let future = async {
        let mut guard = value.lock().unwrap();
        std::future::ready(()).await;
        *guard += 1;
    };
    require_send(future); // deliberate compile error
}''',
['Replacing Mutex with Arc makes every guard Send automatically.','Adding another await releases the guard before that await.','Using the guard after await keeps its non-Send state alive across suspension.'],2,
'The later use retains the guard in the future state. End the critical section before await when the design permits it.',
'Can an async mutex deadlock if a parent holds it while awaiting a child that needs it? Explain cancellation and state invariants separately.')
add('q-async-traits','Async Traits and dyn Compatibility','Native async methods, returned futures and explicit type erasure','interview-api-boundaries',0,
'Native async trait methods and dynamic dispatch are separate interface choices.',
'''Rust supports async methods in traits, but a method returning a hidden future is not directly dispatchable through a trait object under the current dyn-compatibility rules. A generic caller can retain the concrete implementation and future type. A dynamic interface can instead return an explicitly erased future, commonly behind Pin<Box<dyn Future<Output = T> + Send + lifetime>>.

The example deliberately writes that erased interface rather than relying on an attribute macro. Its returned future borrows self, so the lifetime is explicit. Send is also an explicit promise in the returned future type; it is not implied for every native async trait method. Boxing adds an ownership/allocation choice whose tradeoff should match the workload.

A simple noop-waker poll demonstrates only the immediately ready example. Real pending work needs a runtime that arranges wakeups. In an interview, compare a generic implementation, an enum of a closed implementation set and a trait object for an open set. Ask which bounds callers need before choosing an async-trait macro or a boxed interface. Native support does not mean every trait is dyn-compatible, and dynamic dispatch does not inherently require every possible receiver to be heap allocated.''',
'''use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, Waker};
trait Source {
    fn value(&self) -> Pin<Box<dyn Future<Output = u32> + Send + '_>>;
}
struct Fixed(u32);
impl Source for Fixed {
    fn value(&self) -> Pin<Box<dyn Future<Output = u32> + Send + '_>> {
        Box::pin(async move { self.0 })
    }
}
fn main() {
    let fixed = Fixed(7);
    let source: &dyn Source = &fixed;
    let mut future = source.value();
    let mut cx = Context::from_waker(Waker::noop());
    assert_eq!(future.as_mut().poll(&mut cx), Poll::Ready(7));
}''','The trait-object method returns one explicit erased future interface with a borrowing lifetime.',
'Check dyn compatibility, future lifetime and Send bounds independently.',
'Why does this native async method prevent using this trait directly as dyn NativeSource?',
'''trait NativeSource {
    async fn value(&self) -> u32;
}
// Conceptual attempted caller: fn read(source: &dyn NativeSource) {}
// This native async method’s hidden future is not dyn-dispatchable.
fn main() {}''',
['The async method has a hidden future return type that is not dyn-dispatchable here.','Rust forbids async methods in every trait declaration.','The trait becomes dyn-compatible solely by adding Send as a supertrait.'],0,
'Native async traits are supported, but this method is not directly dyn-dispatchable. Use a suitable generic, enum or explicit erased-future interface.',
'If the dynamic interface borrows self, why is returning a static future too strong in general? When does the caller actually require Send?')
add('q-error-boundaries','Error Types at API Boundaries','Absence, invalid input and contextual failure','interview-api-boundaries',1,
'An error type should preserve the distinctions the caller needs to handle.',
'''A missing optional value and an invalid supplied value describe different outcomes. Result<Option<T>, E> can express success with absence, success with a value, or failure. The example converts Option<Result<u16, ParseIntError>> using transpose, preserving all three cases without manufacturing a default port.

At an application boundary you may add contextual information such as a safe field name or a public operation ID. Preserve a useful source error when appropriate and avoid depending on human-readable error strings for control flow. A library can expose typed error cases, while an executable may aggregate errors for reporting. Type erasure through a trait object trades some structured matching for flexibility and may need Send + Sync bounds if the value crosses task boundaries.

In an interview, begin with what the caller can reasonably do: retry, prompt for input, treat absence as normal, or stop. A retry policy also needs to know whether an earlier effect may have committed. Returning Result alone does not make a side effect transactional or idempotent. Do not leak credentials or private paths into a shared diagnostic merely because an error type can store them.''',
'''use std::num::ParseIntError;
fn optional_port(raw: Option<&str>) -> Result<Option<u16>, ParseIntError> {
    raw.map(str::parse::<u16>).transpose()
}
fn main() {
    assert_eq!(optional_port(None), Ok(None));
    assert_eq!(optional_port(Some("8080")), Ok(Some(8080)));
    assert!(optional_port(Some("not-a-port")).is_err());
}''','transpose preserves absence separately from a supplied value that fails to parse.',
'Choose error structure from caller decisions; absence, failure and defaulting are different policies.',
'Which outcome should optional_port(Some("bad")) produce under this contract?',
'''use std::num::ParseIntError;
fn optional_port(raw: Option<&str>) -> Result<Option<u16>, ParseIntError> {
    raw.map(str::parse::<u16>).transpose()
}
fn main() { assert!(optional_port(Some("bad")).is_err()); }''',
['Ok(None), because every parse failure means the field was absent.','Err carrying the parse error, because the supplied value is invalid.','Ok(Some(0)), because Result automatically chooses a numeric default.'],1,
'None represents absence; malformed supplied input follows the error path. Defaults require a separate documented policy.',
'Where would you attach the field name and preserve the source error? Which details should be omitted from a shared public diagnostic?')
add('q-trait-coherence','Orphan Rules and Newtypes','Implementing foreign traits without conflicting implementations','interview-api-boundaries',2,
'A local wrapper creates a distinct type whose behaviour your crate can own.',
'''Rust’s coherence rules restrict trait implementations so that implementations can be selected consistently across crates. The orphan rules broadly require the trait or a relevant implementing type to be local, with additional rules for generic parameters and fundamental types. A type alias does not create a new local type for this purpose.

The example wraps Vec<u8> in a local Bytes type and implements the standard Display trait for that wrapper. It does not attempt to implement Display directly for Vec<u8>. The wrapper also creates an explicit API boundary: you can restrict construction, choose formatting and control which capabilities are exposed. Delegation is a design choice rather than an automatic consequence of wrapping.

In an interview, contrast a local trait implemented for a foreign type with a foreign trait implemented for a local wrapper. Explain why a type alias cannot make an otherwise conflicting implementation valid. Then discuss what a blanket implementation can prevent downstream crates from adding later. The rule is about which implementations exist and can coexist, not a runtime performance penalty. A newtype’s layout or FFI suitability still requires the relevant representation and ABI contract.''',
'''use std::fmt;
struct Bytes(Vec<u8>);
impl fmt::Display for Bytes {
    fn fmt(&self, out: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(out, "{} bytes", self.0.len())
    }
}
fn main() {
    assert_eq!(Bytes(vec![1, 2, 3]).to_string(), "3 bytes");
}''','Display is implemented for a local wrapper, not directly for a foreign Vec type.',
'A newtype creates a distinct local type; an alias only gives an existing type another name.',
'Why does this local Bytes wrapper permit the shown Display implementation?',
'''use std::fmt;
struct Bytes(Vec<u8>);
impl fmt::Display for Bytes {
    fn fmt(&self, out: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(out, "{}", self.0.len())
    }
}
fn main() { assert_eq!(Bytes(vec![1]).to_string(), "1"); }''',
['The wrapper makes the standard Display trait local to this crate.','Any alias of Vec<u8> would create the same local implementation identity.','Bytes is a distinct local implementing type, satisfying the relevant orphan requirement.'],2,
'The trait remains foreign; the implementing wrapper is local. Generic coverage and overlap still need to satisfy coherence rules.',
'Why does type Bytes = Vec<u8> not achieve the same result? What compatibility concern can a blanket impl create?')
add('q-integer-boundaries','Integer Boundaries and Conversion','Checked arithmetic and deliberate narrowing policies','interview-api-boundaries',3,
'Input bounds and arithmetic policy are part of the algorithm’s contract.',
'''Integer operations need a policy when the mathematical result is outside the destination range. checked_add returns None on overflow, wrapping_add uses modular arithmetic, and saturating_add clamps at a boundary. A lossy as conversion can discard information; TryFrom can reject an out-of-range conversion. Choose behaviour that matches the domain instead of depending on the build’s overflow-check settings.

The example checks an addition at u32::MAX and rejects narrowing 300 to u8. It also widens i32 operands before computing their difference. Widening after an overflowing operation is too late. A wider type is sufficient only when the full input-domain calculation fits it; replacing u64 arithmetic with i64 is not a general widening strategy.

In an interview, ask for the input range, the result range and the required failure behaviour. A sum over many elements may overflow even if each element is valid, while a length cast can truncate on large inputs. Boundary tests should cover both sides of a conversion and the exact maximum or minimum. Explain the correctness argument separately from performance measurements and from memory safety: losing numeric information is not automatically undefined behaviour.''',
'''fn main() {
    assert_eq!(u32::MAX.checked_add(1), None);
    assert_eq!(u32::MAX.saturating_add(1), u32::MAX);
    assert!(u8::try_from(300u16).is_err());
    let difference = i64::from(i32::MAX) - i64::from(i32::MIN);
    assert_eq!(difference, 4_294_967_295);
}''','Checked operations report overflow and conversion failure; widening happens before subtraction.',
'Choose the numeric domain and overflow policy explicitly, and widen before the operation when that is the proof.',
'Which result does u8::try_from(300u16) report?',
'''fn main() {
    let value = u8::try_from(300u16);
    assert!(value.is_err());
}''',
['An error, because 300 cannot be represented as u8.','Ok(44), because TryFrom always uses modular narrowing.','A compile error, because integers cannot be converted at runtime.'],0,
'TryFrom checks representability. An as cast follows a different conversion contract and can lose numeric information.',
'Why is i64::from(a - b) unsafe as an overflow strategy for arbitrary i32 inputs, while i64::from(a) - i64::from(b) fits?')
assert len(new)==12
units=[('interview-values','Values, Text and Callbacks','Reason about real value and text boundaries',9,new[:4]),('interview-async-contracts','Future and Callback Contracts','Separate capture, pinning, Send and lock scope',10,new[4:8]),('interview-api-boundaries','API and Numeric Boundaries','Design interfaces with explicit future, error and arithmetic contracts',11,new[8:])]
for order,(id,title,subtitle,level,ids) in enumerate(units,8):
 (ROOT/'units'/f'{id}.json').write_text(json.dumps(dict(id=id,title=title,subtitle=subtitle,level=level,order=order,parentID='interview',lessonIDs=ids,contentDigest=''),indent=2)+'\n')
cpath=ROOT/'course.json';course=json.loads(cpath.read_text());course['unitIDs']+=[u[0] for u in units];course['contentVersion']='1.1.0';course['subtitle']='52 practical Rust interview topics: ownership, async, APIs, systems and live coding';cpath.write_text(json.dumps(course,indent=2)+'\n')
p=ROOT/'provenance.json';r=json.loads(p.read_text());r['contentVersion']='1.1.0';p.write_text(json.dumps(r,indent=2)+'\n')
Path(__file__).with_name('added-ids.json').write_text(json.dumps(new,indent=2)+'\n')
print('Added',len(new),'individual lessons and reasoning checks')
