"""Unit node-ownership: what the garbage collector hid. Authored source for author.py."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


LESSONS = []

# ---------------------------------------------------------------- 12
LESSONS.append(dict(
    id="node-shared-references-to-ownership",
    unit="node-ownership",
    title="Shared references vs ownership",
    concept="Moves instead of shared references",
    minutes=11,
    kind="planned",
    summary="Assigning an object in JavaScript shares it; assigning a `String` or `Vec` in Rust moves it, and the old binding can no longer be used.",
    rule="Each value has one owner: assignment or a by-value parameter moves it, `&T` lends it, and `clone()` makes an independent copy.",
    explanation=[
        "In JavaScript, `const b = a` copies a reference: both names reach the same object, and a change made through `b` is visible through `a`. The garbage collector frees the object once no reference remains. Rust has no garbage collector. Each value has exactly one owner, the owner frees it when it goes out of scope, and `let b = a;` for a `String`, a `Vec` or a struct containing them moves ownership to `b`. Using `a` after the move is E0382.",
        "Function calls follow the same rule. A parameter of type `String` takes ownership, so `shout(name)` moves `name` into the function and the caller cannot print it afterwards. A parameter of type `&str`, or `&T` in general, borrows instead: the function reads the value while the caller keeps it. Returning a value moves ownership back out, which is why `let b = rename(b, \"ferris\");` works.",
        "`clone()` is the explicit copy. For `Crab` it creates a new `String` and a new `Vec<String>` with new `String`s inside, which is closer to `structuredClone` than to `{ ...a }`: spread copies only the outer object and still shares `tags`. Each type decides what `Clone` means, and cloning an `Rc`, for instance, only increments a reference count. Small plain values such as integers, `bool` and `char` are `Copy`: assignment duplicates them and nothing moves.",
        "Moves are checked at compile time and cost nothing at runtime. Moving a `String` copies its pointer, length and capacity, not the text. The point is that exactly one binding is responsible for freeing the buffer, which rules out double frees and use after free without a collector.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        const a = { name: "crab", tags: ["rust"] };
        const b = a;               // a second name for the same object
        b.name = "ferris";

        const shallow = { ...a };  // new outer object, same tags array
        shallow.tags.push("cargo");

        const deep = structuredClone(a);
        deep.tags.push("tokio");

        console.log(a.name, a.tags, deep.tags);
    '''),
    from_stdout="ferris [ 'rust', 'cargo' ] [ 'rust', 'cargo', 'tokio' ]\n",
    from_caption="Three names reach one object; spread copies only the top level, while `structuredClone` also copies the nested array.",
    example=code(r'''
        #[derive(Clone, Debug)]
        struct Crab {
            name: String,
            tags: Vec<String>,
        }

        fn rename(mut crab: Crab, name: &str) -> Crab {
            crab.name = name.to_string();
            crab
        }

        fn main() {
            let a = Crab { name: String::from("crab"), tags: vec![String::from("rust")] };
            let b = a; // move: `a` can no longer be used
            let mut copy = b.clone(); // a new Vec and new Strings
            copy.tags.push(String::from("cargo"));
            let b = rename(b, "ferris"); // ownership goes in and comes back
            println!("{b:?}");
            println!("{:?}", copy.tags);
        }
    '''),
    example_stdout="Crab { name: \"ferris\", tags: [\"rust\"] }\n[\"rust\", \"cargo\"]\n",
    example_caption="`let b = a` moves the crab, `clone` makes an independent copy, and `rename` takes ownership and gives it back.",
    contrasts=[
        ("`const b = a` makes a second reference to the same object.",
         "`let b = a;` moves a `String` or `Vec`; using `a` afterwards is E0382."),
        ("Passing an object to a function shares it with the caller.",
         "A `String` parameter takes ownership; take `&str` so the caller keeps it."),
        ("`{ ...a }` copies the outer object and shares nested arrays.",
         "`a.clone()` follows each type's `Clone`; for a `Vec<String>` it copies every `String`."),
        ("The garbage collector frees unreachable objects at some later point.",
         "The owner frees the value when its scope ends, deterministically."),
    ],
    credits=["ownership/ownership", "ownership/move-functions"],
    practice=code(r'''
        fn shout(text: String) -> String {
            text.to_uppercase()
        }

        fn main() {
            let name = String::from("ferris");
            let loud = shout(name);
            println!("{loud} {name}");
        }
    '''),
    practice_expect={"errors": ["E0382"]},
    question="In the practice code, what is the smallest change that keeps `name` usable after the call, without cloning?",
    answers=[
        "Make the parameter `text: &str` and call `shout(&name)`",
        "Declare `let mut name`",
        "Wrap the call in a block: `{ shout(name) }`",
    ],
    correct=0,
    feedback="A `&str` parameter only borrows, so ownership of `name` stays with the caller. `mut` does not prevent a move.",
    task="Fix the practice code twice: once by borrowing with `&str`, once by cloning. Then decide which fix fits a function that only reads its input, and which fits one that must keep the text after it returns.",
    success="You predicted E0382 for the original code, and you can explain why borrowing avoids both the move and the copy.",
    misconception="“`let b = a;` gives the same `String` a second name, like a JavaScript reference.”",
    correction="For a `String`, `let b = a;` moves ownership, and `a` can no longer be used. Share it with a borrow `&a`, or copy it with `a.clone()`.",
    trace=[
        ("Follow the owner", "`a` owns the `Crab`. After `let b = a;`, `b` is the only owner and `a` cannot be used."),
        ("Separate the copy", "`b.clone()` builds a new `Crab` with its own `Vec`. Pushing `cargo` into `copy.tags` cannot affect `b`."),
        ("Compare with evidence", "Run it: `Crab { name: \"ferris\", tags: [\"rust\"] }`, then `[\"rust\", \"cargo\"]`. Add `println!(\"{a:?}\");` at the end and read E0382, which points at the move."),
    ],
    transfer="Change `rename` to `fn rename(crab: &mut Crab, name: &str)` and call it as `rename(&mut b, \"ferris\")`. Decide which signature you would expose from a library, and why.",
    connections=[("previous", "UTF-16 strings vs UTF-8 String", "UTF-8 bytes, chars and lengths"),
                 ("next", "Mutating arguments vs borrowing", "Shared and mutable borrows")],
    recall=[
        dict(question="Why is the last line rejected?",
             code=code(r'''
                 let tags = vec![String::from("rust")];
                 let all = tags;
                 println!("{}", tags.len());
             '''),
             answer="`let all = tags;` moved the vector, so `tags` no longer owns anything: E0382, borrow of moved value. Use `all.len()`, borrow with `let all = &tags;`, or clone if two independent vectors are really needed.",
             expect={"errors": ["E0382"]}),
        dict(question="Why does `let y = x;` leave `x` usable when `x` is an `i32`, but not when it is a `String`?",
             answer="`i32` is `Copy`: assignment duplicates the bits and there is nothing to free. A `String` owns a heap buffer, so assignment moves ownership to keep exactly one owner responsible for freeing it. `Copy` is only implemented for types where a bitwise copy is safe."),
    ],
))

# ---------------------------------------------------------------- 13
LESSONS.append(dict(
    id="node-mutation-to-borrowing",
    unit="node-ownership",
    title="Mutating arguments vs borrowing",
    concept="Shared and mutable borrows",
    minutes=12,
    kind="runnable",
    summary="A function that changes its argument takes `&mut T`, and one that reads takes `&T`. Many shared borrows or one mutable borrow may exist, never both at once.",
    rule="`&T` lends read-only access and `&mut T` lends exclusive write access; neither transfers ownership, and the two never overlap.",
    explanation=[
        "JavaScript passes objects by sharing, so `addUnique(tags, \"cargo\")` silently changes the caller's array. Rust makes the intent part of the signature. `fn add_unique(tags: &mut Vec<String>, tag: &str)` says the function will modify the vector and only read the tag, and the call site repeats it: `add_unique(&mut tags, \"cargo\")`. The caller still owns `tags` afterwards.",
        "Borrows follow one rule: any number of shared references `&T`, or exactly one mutable reference `&mut T`, but not both at the same time. A mutable borrow is exclusive; while it exists, nothing else may read or write the value. That rule is what lets Rust rule out data races and iterator invalidation at compile time.",
        "The JavaScript loop shows what the rule prevents. `for (const n of queue) queue.push(...)` keeps visiting the items it appends, so a slightly different condition never ends. In Rust, `for n in &queue` holds a shared borrow for the whole loop, and `queue.push` needs `&mut queue`, so rustc reports E0502; pushing could also reallocate the buffer the loop is reading. An index loop that rereads `queue.len()` on every pass makes the growing behaviour explicit.",
        "Ask for the least access a function needs. Take `&[String]` rather than `&Vec<String>` to read, `&mut [String]` to change elements in place, and `&mut Vec<String>` only when the function must push or remove. Assigning through a shared reference is E0594; the fix belongs in the signature, not in the body.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        function addUnique(tags, tag) {
          if (!tags.includes(tag)) tags.push(tag); // mutates the caller's array
          return tags.length;
        }

        const tags = ["rust"];
        console.log(addUnique(tags, "cargo"), tags);

        const queue = [1];
        for (const n of queue) {
          if (n < 4) queue.push(n + 1); // the loop sees the new items
        }
        console.log(queue);
    '''),
    from_stdout="2 [ 'rust', 'cargo' ]\n[ 1, 2, 3, 4 ]\n",
    from_caption="`addUnique` silently mutates the caller's array, and `for...of` keeps visiting items pushed during the loop.",
    example=code(r'''
        fn add_unique(tags: &mut Vec<String>, tag: &str) -> usize {
            if !tags.iter().any(|t| t == tag) {
                tags.push(tag.to_string());
            }
            tags.len()
        }

        fn longest(tags: &[String]) -> Option<&str> {
            tags.iter().map(|t| t.as_str()).max_by_key(|t| t.len())
        }

        fn main() {
            let mut tags = vec![String::from("rust")];
            println!("{}", add_unique(&mut tags, "cargo"));
            println!("{tags:?} {:?}", longest(&tags));

            let mut queue = vec![1];
            let mut i = 0;
            while i < queue.len() {
                if queue[i] < 4 {
                    queue.push(queue[i] + 1);
                }
                i += 1;
            }
            println!("{queue:?}");
        }
    '''),
    example_stdout="2\n[\"rust\", \"cargo\"] Some(\"cargo\")\n[1, 2, 3, 4]\n",
    example_caption="`add_unique` borrows mutably, `longest` borrows shared, and the index loop makes the growth explicit.",
    contrasts=[
        ("Any function can mutate an array it receives.",
         "Only a `&mut` parameter can mutate, and the call site writes `&mut tags`."),
        ("Appending inside `for...of` over the same array keeps iterating the new items.",
         "`push` inside `for n in &queue` is E0502, because a shared borrow is alive."),
        ("Two variables can change one object at the same time.",
         "One `&mut` at a time, and no `&` while it exists."),
        ("Passing an array never changes who owns it.",
         "Borrowing never transfers ownership either; only a by-value parameter does."),
    ],
    credits=["basics/references-intro", "ownership/borrowing", "ownership/mutable-borrows"],
    practice=code(r'''
        fn main() {
            let mut queue = vec![1];
            for n in &queue {
                if *n < 4 {
                    queue.push(n + 1);
                }
            }
            println!("{queue:?}");
        }
    '''),
    practice_expect={"errors": ["E0502"]},
    question="Why does rustc reject `queue.push(n + 1)` inside `for n in &queue`?",
    answers=[
        "`push` is not allowed inside any loop",
        "`n` is a moved value",
        "The loop holds a shared borrow of `queue`, and `push` needs exclusive `&mut` access while that borrow is alive",
    ],
    correct=2,
    feedback="This is E0502. The shared borrow lasts for the whole loop, a mutable borrow cannot overlap it, and the push might reallocate the buffer being read.",
    task="Port the JavaScript `renameAll` and `countMatches` shown at the top of solution.rs. `rename_all` changes matching names in place through `&mut [String]` and returns how many matched; `count_matches` only reads through `&[String]`. The caller keeps its vector. In the Crabrix app, open the compiler lab and complete the supplied functions in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including no match and renaming a name to itself. Printing a success message alone does not complete this lab.",
    misconception="“Passing `&mut tags` hands the vector over to the function, like a move.”",
    correction="`&mut` lends exclusive access for the duration of the call. Ownership stays with the caller, who can use `tags` again once the borrow ends.",
    trace=[
        ("Read the signatures", "`add_unique` takes `&mut Vec<String>` because it pushes. `longest` takes `&[String]` because it only reads."),
        ("Follow the borrows", "`add_unique(&mut tags, \"cargo\")` borrows exclusively for one call. After it returns, `&tags` can be borrowed shared by `longest` and the `println!`."),
        ("Compare with evidence", "Run it: `2`, `[\"rust\", \"cargo\"] Some(\"cargo\")`, then `[1, 2, 3, 4]`. Replace the `while` loop with `for n in &queue` and read E0502."),
    ],
    transfer="Keep a reference with `let first = &tags[0];`, call `add_unique(&mut tags, \"tokio\")`, then print `first`. Predict the error code, then reorder the lines so the program compiles.",
    connections=[("previous", "Shared references vs ownership", "Moves instead of shared references"),
                 ("next", "TypeScript interfaces vs traits", "Nominal traits instead of structural interfaces")],
    recall=[
        dict(question="Why is this rejected, and what is the smallest fix?",
             code=code(r'''
                 let mut v = vec![1, 2];
                 let first = &v[0];
                 v.push(3);
                 println!("{first}");
             '''),
             answer="`first` is a shared borrow that is still used after `push`, which needs a mutable borrow: E0502. The push may reallocate and leave `first` dangling. Print `first` before the push, or copy the value with `let first = v[0];`.",
             expect={"errors": ["E0502"]}),
        dict(question="Why should a read-only function take `&[String]` instead of `&Vec<String>`?",
             answer="`&[String]` accepts a borrowed `Vec`, an array or any slice of either, and promises only read access to the elements. `&Vec<String>` adds nothing a reader can use and rejects arrays and subslices. Use `&mut Vec<String>` only when the function must push or remove."),
    ],
    challenge=dict(
        function="rename_all",
        starter=code(r'''
            // JavaScript original:
            // function renameAll(names, from, to) {
            //   let changed = 0;
            //   for (let i = 0; i < names.length; i++) {
            //     if (names[i] === from) { names[i] = to; changed++; }
            //   }
            //   return changed;
            // }
            // function countMatches(names, wanted) {
            //   return names.filter((n) => n === wanted).length;
            // }
            pub fn rename_all(names: &mut [String], from: &str, to: &str) -> usize {
                todo!("implement the contract")
            }

            pub fn count_matches(names: &[String], wanted: &str) -> usize {
                todo!("implement the contract")
            }
        '''),
        harness=code(r'''
            mod solution;

            fn names(list: &[&str]) -> Vec<String> {
                list.iter().map(|name| name.to_string()).collect()
            }

            fn main() {
                let mut team = names(&["ana", "bo", "ana"]);
                assert_eq!(solution::rename_all(&mut team, "ana", "eva"), 2, "case 1");
                assert_eq!(team, names(&["eva", "bo", "eva"]), "case 2");
                assert_eq!(solution::count_matches(&team, "eva"), 2, "case 3");
                assert_eq!(solution::rename_all(&mut team, "zed", "x"), 0, "case 4");
                assert_eq!(solution::rename_all(&mut team, "bo", "bo"), 1, "case 5");
                assert_eq!(team, names(&["eva", "bo", "eva"]), "case 6");
                let mut empty: Vec<String> = Vec::new();
                assert_eq!(solution::rename_all(&mut empty, "a", "b"), 0, "case 7");
                assert_eq!(solution::count_matches(&team[..1], "eva"), 1, "case 8");

                println!("PASS node-mutation-to-borrowing");
            }
        '''),
        cases=[
            ("visible", "rename_all(&mut [\"ana\", \"bo\", \"ana\"], \"ana\", \"eva\")", "2, and the caller sees [\"eva\", \"bo\", \"eva\"]"),
            ("semantic", "count_matches(&team, \"eva\")", "2"),
            ("boundary", "rename_all(&mut team, \"zed\", \"x\")", "0"),
            ("boundary", "rename_all(&mut team, \"bo\", \"bo\")", "1, names unchanged"),
            ("boundary", "rename_all(&mut [], \"a\", \"b\")", "0"),
            ("semantic", "count_matches(&team[..1], \"eva\")", "1"),
        ],
        required=["pub fn count_matches"],
        solution=code(r'''
            pub fn rename_all(names: &mut [String], from: &str, to: &str) -> usize {
                let mut changed = 0;
                for name in names.iter_mut() {
                    if name == from {
                        *name = to.to_string();
                        changed += 1;
                    }
                }
                changed
            }

            pub fn count_matches(names: &[String], wanted: &str) -> usize {
                names.iter().filter(|name| *name == wanted).count()
            }
        '''),
        wrong=[
            ("assigns through a shared iterator", code(r'''
                pub fn rename_all(names: &mut [String], from: &str, to: &str) -> usize {
                    let mut changed = 0;
                    for name in names.iter() {
                        if name == from {
                            *name = to.to_string();
                            changed += 1;
                        }
                    }
                    changed
                }

                pub fn count_matches(names: &[String], wanted: &str) -> usize {
                    names.iter().filter(|name| *name == wanted).count()
                }
            ''')),
            ("renames a copy instead of the caller's names", code(r'''
                pub fn rename_all(names: &mut [String], from: &str, to: &str) -> usize {
                    let mut copy = names.to_vec();
                    let mut changed = 0;
                    for name in copy.iter_mut() {
                        if name == from {
                            *name = to.to_string();
                            changed += 1;
                        }
                    }
                    changed
                }

                pub fn count_matches(names: &[String], wanted: &str) -> usize {
                    names.iter().filter(|name| *name == wanted).count()
                }
            ''')),
        ],
        js_lang="javascript",
        js_original=code(r'''
            function renameAll(names, from, to) {
              let changed = 0;
              for (let i = 0; i < names.length; i++) {
                if (names[i] === from) { names[i] = to; changed++; }
              }
              return changed;
            }
            function countMatches(names, wanted) {
              return names.filter((n) => n === wanted).length;
            }
            const team = ["ana", "bo", "ana"];
            const first = renameAll(team, "ana", "eva");
            const afterFirst = [...team];
        '''),
        js_checks=[("first", 2), ("afterFirst", ["eva", "bo", "eva"]), ("countMatches(team, \"eva\")", 2),
                   ("renameAll(team, \"zed\", \"x\")", 0), ("renameAll(team, \"bo\", \"bo\")", 1),
                   ("renameAll([], \"a\", \"b\")", 0), ("countMatches(team.slice(0, 1), \"eva\")", 1)],
    ),
))

# ---------------------------------------------------------------- 14
LESSONS.append(dict(
    id="node-interfaces-to-traits",
    unit="node-ownership",
    title="TypeScript interfaces vs traits",
    concept="Nominal traits instead of structural interfaces",
    minutes=13,
    kind="runnable",
    summary="A TypeScript interface is satisfied by any value with the right shape; a Rust trait is satisfied only by types that explicitly `impl` it.",
    rule="A type implements a trait only through an explicit `impl`; use a generic bound for static dispatch over one type and `dyn Trait` for a collection of mixed types.",
    explanation=[
        "TypeScript interfaces are structural. The object literals in the example have no `implements` clause, yet both are `Shape`s because they have `area` and `name`. Rust traits are nominal: `Square` satisfies `Shape` only after `impl Shape for Square { ... }`, and an inherent method with the same name does not count. That is the E0277 in the practice code, the trait bound `Square: Shape` is not satisfied.",
        "A trait bound plays the role of `<T extends Shape>`. `fn total_area<T: Shape>(items: &[T])` is generic: the compiler generates a separate copy for each concrete `T` it is used with, and the calls are dispatched statically. Every item in that slice must be the same `T`, so it cannot hold a square and a rectangle together.",
        "For a mixed collection, the counterpart of an array of interface values, use trait objects: `Vec<Box<dyn Shape>>`. Each element is a pointer to some type that implements `Shape` plus a table of its methods, and calls are dispatched at runtime, which is how every JavaScript method call works anyway. Neither form is automatically faster: generics can grow code size, and trait objects add an indirection.",
        "Traits cover other TypeScript patterns too. Default methods replace a shared base class, `impl Display for T` replaces `toString`, and implementing a standard trait such as `PartialOrd` plugs your type into existing generic code. You may implement your own trait for a foreign type such as `u32`, but not a foreign trait for a foreign type.",
    ],
    from_lang="typescript",
    from_label="TypeScript",
    from_code=code(r'''
        interface Shape {
          area(): number;
          name(): string;
        }

        function largest(shapes: Shape[]): string | undefined {
          let best: Shape | undefined;
          for (const s of shapes) if (!best || s.area() > best.area()) best = s;
          return best?.name();
        }

        // No "implements" needed: any value with the right members is a Shape.
        const square = { area: () => 9, name: () => "square" };
        const rect = { w: 2, h: 5, area() { return this.w * this.h; }, name: () => "rect" };
        console.log(largest([square, rect]), largest([]));
    '''),
    from_stdout="rect undefined\n",
    from_caption="Structural typing: two object literals count as `Shape`s just by having the right members.",
    example=code(r'''
        trait Shape {
            fn area(&self) -> u32;
            fn name(&self) -> &str;
        }

        struct Square { side: u32 }
        struct Rect { w: u32, h: u32 }

        impl Shape for Square {
            fn area(&self) -> u32 { self.side * self.side }
            fn name(&self) -> &str { "square" }
        }

        impl Shape for Rect {
            fn area(&self) -> u32 { self.w * self.h }
            fn name(&self) -> &str { "rect" }
        }

        fn total_area<T: Shape>(items: &[T]) -> u32 {
            items.iter().map(|s| s.area()).sum()
        }

        fn largest(shapes: &[Box<dyn Shape>]) -> Option<&str> {
            shapes.iter().max_by_key(|s| s.area()).map(|s| s.name())
        }

        fn main() {
            let shapes: Vec<Box<dyn Shape>> = vec![Box::new(Square { side: 3 }), Box::new(Rect { w: 2, h: 5 })];
            println!("{:?} {}", largest(&shapes), total_area(&[Square { side: 2 }, Square { side: 1 }]));
        }
    '''),
    example_stdout="Some(\"rect\") 5\n",
    example_caption="Explicit `impl` blocks make both structs `Shape`s; `total_area` is generic, and `largest` takes trait objects.",
    contrasts=[
        ("Any object with `area()` and `name()` is a `Shape`.",
         "Only a type with `impl Shape for T` is a `Shape`; a method with the same name is not enough."),
        ("`function f<T extends Shape>(x: T)`",
         "`fn f<T: Shape>(x: &T)`, compiled separately for each concrete `T`."),
        ("A `Shape[]` can hold any mix of shapes.",
         "Mixed values need `Vec<Box<dyn Shape>>`, dispatched at runtime."),
        ("`implements` is optional documentation.",
         "The `impl` block is the implementation; without it the type has none of the trait's methods."),
    ],
    credits=["ownership/traits"],
    practice=code(r'''
        trait Shape {
            fn area(&self) -> u32;
        }

        struct Square {
            side: u32,
        }

        impl Square {
            fn area(&self) -> u32 {
                self.side * self.side
            }
        }

        fn print_area<T: Shape>(shape: &T) {
            println!("{}", shape.area());
        }

        fn main() {
            print_area(&Square { side: 3 });
        }
    '''),
    practice_expect={"errors": ["E0277"], "messages": ["the trait bound `Square: Shape` is not satisfied"]},
    question="Which signature lets one call handle a list that mixes `Book` and `Coffee` values?",
    answers=[
        "`fn total<T: Priced>(items: &[T]) -> u64`",
        "`fn total(items: &[Box<dyn Priced>]) -> u64`",
        "`fn total(items: &[impl Priced]) -> u64`",
    ],
    correct=1,
    feedback="A generic type parameter, written either way, is one concrete type per call. A slice of `Box<dyn Priced>` holds different types behind one trait.",
    task="Port the TypeScript code shown at the top of solution.rs. Implement `Priced` for `Book` and for `Coffee` (250 cents plus 50 per size step, labelled `coffee`), write the generic `total`, and write `cheapest` over trait objects, returning the label of the first cheapest item as the TypeScript loop does. In the Crabrix app, open the compiler lab and complete the supplied code in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including an empty list and a tie for the cheapest item. Printing a success message alone does not complete this lab.",
    misconception="“If `Square` has an `area` method, it can be passed wherever a `Shape` is expected, as in TypeScript.”",
    correction="Rust checks trait implementations, not shapes. Write `impl Shape for Square` and put the method inside that block.",
    trace=[
        ("Find the impls", "`Square` and `Rect` each get an `impl Shape` block. Without them, neither could be passed to `total_area` or boxed as a `dyn Shape`."),
        ("Compare the two calls", "`total_area(&[Square { side: 2 }, Square { side: 1 }])` uses one concrete type. `largest(&shapes)` walks boxes that point to different types."),
        ("Compare with evidence", "Run it: `Some(\"rect\") 5`. Try `total_area(&[Square { side: 2 }, Rect { w: 1, h: 1 }])` and read the mismatched types error."),
    ],
    transfer="Add a default method `fn describe(&self) -> String { format!(\"{} of area {}\", self.name(), self.area()) }` to `Shape`, call it on both shapes, then override it for `Rect` only.",
    connections=[("previous", "Mutating arguments vs borrowing", "Shared and mutable borrows"),
                 ("next", "try/catch vs Result", "Errors as Result values")],
    recall=[
        dict(question="Why is the call rejected, and what fixes it?",
             code=code(r'''
                 trait Named { fn name(&self) -> String; }
                 struct User { login: String }
                 impl User {
                     fn name(&self) -> String { self.login.clone() }
                 }
                 fn greet<T: Named>(x: &T) { println!("hi {}", x.name()); }
                 greet(&User { login: String::from("ana") });
             '''),
             answer="`User` has an inherent `name` method but no `impl Named for User`, so the bound is not satisfied: E0277. Traits are nominal. Move the method into `impl Named for User { fn name(&self) -> String { ... } }`.",
             expect={"errors": ["E0277"]}),
        dict(question="When is `Vec<Box<dyn Shape>>` the right choice over a generic `Vec<T>` with `T: Shape`?",
             answer="When one collection must hold different concrete types, or when the type is only known at runtime. Generics fix one `T` per instantiation and are compiled into a separate copy for each; trait objects store a pointer plus a method table and dispatch at runtime. Measure before assuming either is faster."),
    ],
    challenge=dict(
        function="cheapest",
        starter=code(r'''
            // TypeScript original:
            // interface Priced { cents(): number; label(): string }
            // function total<T extends Priced>(items: T[]): number {
            //   return items.reduce((sum, item) => sum + item.cents(), 0);
            // }
            // function cheapest(items: Priced[]): string | undefined {
            //   let best: Priced | undefined;
            //   for (const item of items) if (!best || item.cents() < best.cents()) best = item;
            //   return best?.label();
            // }
            // A book costs its own price; a coffee costs 250 cents plus 50 per size step.
            pub trait Priced {
                fn cents(&self) -> u64;
                fn label(&self) -> String;
            }

            pub struct Book {
                pub title: String,
                pub cents: u64,
            }

            pub struct Coffee {
                pub size: u32,
            }

            impl Priced for Book {
                fn cents(&self) -> u64 {
                    todo!("implement the contract")
                }
                fn label(&self) -> String {
                    todo!("implement the contract")
                }
            }

            impl Priced for Coffee {
                fn cents(&self) -> u64 {
                    todo!("implement the contract")
                }
                fn label(&self) -> String {
                    todo!("implement the contract")
                }
            }

            pub fn total<T: Priced>(items: &[T]) -> u64 {
                todo!("implement the contract")
            }

            pub fn cheapest(items: &[Box<dyn Priced>]) -> Option<String> {
                todo!("implement the contract")
            }
        '''),
        harness=code(r'''
            mod solution;

            use solution::{Book, Coffee, Priced};

            fn book(title: &str, cents: u64) -> Book {
                Book { title: title.to_string(), cents }
            }

            fn main() {
                assert_eq!(solution::total(&[book("Rust", 3900), book("Node", 2900)]), 6800, "case 1");
                assert_eq!(solution::total::<Coffee>(&[]), 0, "case 2");
                assert_eq!(solution::total(&[Coffee { size: 0 }, Coffee { size: 2 }]), 600, "case 3");
                let mixed: Vec<Box<dyn Priced>> = vec![
                    Box::new(book("Rust", 400)),
                    Box::new(Coffee { size: 3 }),
                    Box::new(Coffee { size: 1 }),
                ];
                assert_eq!(solution::cheapest(&mixed), Some(String::from("coffee")), "case 4");
                let tie: Vec<Box<dyn Priced>> = vec![Box::new(book("A", 300)), Box::new(Coffee { size: 1 })];
                assert_eq!(solution::cheapest(&tie), Some(String::from("A")), "case 5");
                assert_eq!(solution::cheapest(&[]), None, "case 6");

                println!("PASS node-interfaces-to-traits");
            }
        '''),
        cases=[
            ("visible", "total(&[Book 3900, Book 2900])", "6800"),
            ("boundary", "total::<Coffee>(&[])", "0"),
            ("semantic", "total(&[Coffee { size: 0 }, Coffee { size: 2 }])", "600"),
            ("visible", "cheapest(&[Book 400, Coffee 3, Coffee 1])", "Some(\"coffee\")"),
            ("boundary", "cheapest(&[Book \"A\" 300, Coffee 1]): a tie keeps the first", "Some(\"A\")"),
            ("boundary", "cheapest(&[])", "None"),
        ],
        required=["impl Priced for Coffee"],
        solution=code(r'''
            pub trait Priced {
                fn cents(&self) -> u64;
                fn label(&self) -> String;
            }

            pub struct Book {
                pub title: String,
                pub cents: u64,
            }

            pub struct Coffee {
                pub size: u32,
            }

            impl Priced for Book {
                fn cents(&self) -> u64 {
                    self.cents
                }
                fn label(&self) -> String {
                    self.title.clone()
                }
            }

            impl Priced for Coffee {
                fn cents(&self) -> u64 {
                    250 + 50 * u64::from(self.size)
                }
                fn label(&self) -> String {
                    String::from("coffee")
                }
            }

            pub fn total<T: Priced>(items: &[T]) -> u64 {
                items.iter().map(|item| item.cents()).sum()
            }

            pub fn cheapest(items: &[Box<dyn Priced>]) -> Option<String> {
                items.iter().min_by_key(|item| item.cents()).map(|item| item.label())
            }
        '''),
        wrong=[
            ("a <= comparison keeps the last cheapest item", code(r'''
                pub trait Priced {
                    fn cents(&self) -> u64;
                    fn label(&self) -> String;
                }

                pub struct Book {
                    pub title: String,
                    pub cents: u64,
                }

                pub struct Coffee {
                    pub size: u32,
                }

                impl Priced for Book {
                    fn cents(&self) -> u64 {
                        self.cents
                    }
                    fn label(&self) -> String {
                        self.title.clone()
                    }
                }

                impl Priced for Coffee {
                    fn cents(&self) -> u64 {
                        250 + 50 * u64::from(self.size)
                    }
                    fn label(&self) -> String {
                        String::from("coffee")
                    }
                }

                pub fn total<T: Priced>(items: &[T]) -> u64 {
                    items.iter().map(|item| item.cents()).sum()
                }

                pub fn cheapest(items: &[Box<dyn Priced>]) -> Option<String> {
                    let mut best: Option<&Box<dyn Priced>> = None;
                    for item in items {
                        if best.map_or(true, |b| item.cents() <= b.cents()) {
                            best = Some(item);
                        }
                    }
                    best.map(|item| item.label())
                }
            ''')),
            ("structural habit: methods on Coffee without impl Priced", code(r'''
                pub trait Priced {
                    fn cents(&self) -> u64;
                    fn label(&self) -> String;
                }

                pub struct Book {
                    pub title: String,
                    pub cents: u64,
                }

                pub struct Coffee {
                    pub size: u32,
                }

                impl Priced for Book {
                    fn cents(&self) -> u64 {
                        self.cents
                    }
                    fn label(&self) -> String {
                        self.title.clone()
                    }
                }

                impl Coffee {
                    pub fn cents(&self) -> u64 {
                        250 + 50 * u64::from(self.size)
                    }
                    pub fn label(&self) -> String {
                        String::from("coffee")
                    }
                }

                pub fn total<T: Priced>(items: &[T]) -> u64 {
                    items.iter().map(|item| item.cents()).sum()
                }

                pub fn cheapest(items: &[Box<dyn Priced>]) -> Option<String> {
                    items.iter().min_by_key(|item| item.cents()).map(|item| item.label())
                }
            ''')),
        ],
        js_lang="typescript",
        js_original=code(r'''
            interface Priced { cents(): number; label(): string }
            function total<T extends Priced>(items: T[]): number {
              return items.reduce((sum, item) => sum + item.cents(), 0);
            }
            function cheapest(items: Priced[]): string | undefined {
              let best: Priced | undefined;
              for (const item of items) if (!best || item.cents() < best.cents()) best = item;
              return best?.label();
            }
            const book = (title: string, price: number): Priced => ({ cents: () => price, label: () => title });
            const coffee = (size: number): Priced => ({ cents: () => 250 + 50 * size, label: () => "coffee" });
        '''),
        js_checks=[("total([book(\"Rust\", 3900), book(\"Node\", 2900)])", 6800), ("total([])", 0),
                   ("total([coffee(0), coffee(2)])", 600),
                   ("cheapest([book(\"Rust\", 400), coffee(3), coffee(1)])", "coffee"),
                   ("cheapest([book(\"A\", 300), coffee(1)])", "A"), ("cheapest([]) ?? null", None)],
    ),
))
