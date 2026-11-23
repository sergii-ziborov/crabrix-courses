"""Unit node-data: data shapes. Authored source for author.py."""

from textwrap import dedent


def code(text: str) -> str:
    return dedent(text).strip("\n")


LESSONS = []

# ---------------------------------------------------------------- 6
LESSONS.append(dict(
    id="node-objects-to-structs",
    unit="node-data",
    title="Classes and objects vs structs",
    concept="Data in structs, behaviour in impl blocks",
    minutes=11,
    kind="runnable",
    summary="A class becomes a `struct` for the data and an `impl` block for the methods, and each method's receiver says whether it reads, changes or consumes the value.",
    rule="`&self` reads, `&mut self` modifies and `self` consumes: the receiver tells the caller what a method does to the value.",
    explanation=[
        "A JavaScript class bundles fields, methods and a prototype chain, and every method receives the same mutable `this`. Rust splits the parts. A `struct` declares the fields and their types, and an `impl` block adds functions. There is no constructor keyword: `new` is an ordinary associated function returning `Self`, called as `Counter::new(2)`. There is no inheritance either; shared behaviour comes from traits.",
        "The receiver is the part without a JavaScript equivalent. `fn is_full(&self)` only reads, so it works through a shared reference. `fn increment(&mut self)` changes fields, so the caller needs a `mut` binding and exclusive access for the duration of the call. `fn close(self)` takes ownership: after `wallet.close()` the caller can no longer use `wallet`, which is how Rust says \"this object is finished\" without a runtime flag.",
        "Fields are private to their module by default. Outside it, `c.count = 99` does not compile unless the field is `pub`, so an invariant such as `count <= limit` is enforced by the methods rather than by convention. Inside the defining module, as in this single-file example, `main` can still read `c.count`.",
        "A struct literal must set every field; there is no `undefined` property. Optional fields are `Option<T>`, and defaults come from `#[derive(Default)]` or an explicit constructor. Printing a struct with `{:?}` needs `#[derive(Debug)]`, and comparing two with `==` needs `PartialEq`.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        class Counter {
          constructor(limit) { this.count = 0; this.limit = limit; }
          increment() {
            if (this.count < this.limit) this.count += 1;
            return this.count;
          }
          isFull() { return this.count === this.limit; }
        }

        const c = new Counter(2);
        c.increment(); c.increment(); c.increment();
        console.log(c.count, c.isFull());
        c.count = 99;                 // any caller may write any field
        console.log(c.isFull());
    '''),
    from_stdout="2 true\nfalse\n",
    from_caption="Every method shares one mutable `this`, and nothing stops a caller from writing `count` directly.",
    example=code(r'''
        struct Counter {
            count: u32,
            limit: u32,
        }

        impl Counter {
            fn new(limit: u32) -> Self {
                Counter { count: 0, limit }
            }

            fn increment(&mut self) -> u32 {
                if self.count < self.limit {
                    self.count += 1;
                }
                self.count
            }

            fn is_full(&self) -> bool {
                self.count == self.limit
            }
        }

        fn main() {
            let mut c = Counter::new(2);
            c.increment();
            c.increment();
            c.increment();
            println!("{} {}", c.count, c.is_full());
        }
    '''),
    example_stdout="2 true\n",
    example_caption="`increment` borrows mutably, `is_full` only reads, and `new` is a plain associated function.",
    contrasts=[
        ("Every method gets the same mutable `this`.",
         "Each method declares `&self`, `&mut self` or `self`, and the compiler enforces that choice."),
        ("`constructor(limit)` runs on `new Counter(2)`.",
         "`fn new(limit: u32) -> Self` is an ordinary function, called as `Counter::new(2)`."),
        ("Any caller can write `c.count = 99`.",
         "Fields are private outside their module unless they are marked `pub`."),
        ("A missing property reads as `undefined`.",
         "A struct literal must set every field; optional data is `Option<T>`."),
    ],
    credits=["basics/structs", "basics/methods-intro"],
    practice=code(r'''
        struct Counter {
            count: u32,
        }

        impl Counter {
            fn finish(self) -> u32 {
                self.count
            }
        }

        fn main() {
            let c = Counter { count: 2 };
            println!("{}", c.finish());
            println!("{}", c.finish());
        }
    '''),
    practice_expect={"errors": ["E0382"]},
    question="What does `fn finish(self) -> u32` tell a caller that `fn count(&self) -> u32` does not?",
    answers=[
        "The call consumes the value, so it cannot be used afterwards",
        "The method is static and has no `this`",
        "The method can be called only once per program",
    ],
    correct=0,
    feedback="`self` by value moves the struct into the method. The second `c.finish()` is E0382, use of a moved value.",
    task="Port the JavaScript `Wallet` class shown at the top of solution.rs: `new`, `deposit`, `withdraw` (which refuses more than the balance and returns `false`), `balance` and `close` (which returns the final balance and ends the wallet). Keep the receivers in the starter: `balance` must work through a shared reference and `close` consumes the wallet. In the Crabrix app, open the compiler lab and complete the supplied methods in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including withdrawing the exact balance and reading it through `&Wallet`. Printing a success message alone does not complete this lab.",
    misconception="“Every method can change the object, as with `this` in a class.”",
    correction="Only methods that take `&mut self` or `self` can change it. A `&self` method is read-only, and rustc rejects a field assignment inside it with E0594.",
    trace=[
        ("Read the receivers", "`new` has no receiver. `increment(&mut self)` changes `count`, and `is_full(&self)` only reads it."),
        ("Check the caller", "`let mut c` is required because `increment` borrows `c` mutably. `is_full` alone would work on an immutable binding."),
        ("Compare with evidence", "Run it: `2 true`, because the limit refused the third `increment`. Make `is_full` assign `self.count = 0;` and read E0594."),
    ],
    transfer="Add `fn reset(self) -> Counter` that returns a fresh counter with the same limit, and call it as `let c = c.reset();`. Explain why shadowing `c` reads naturally here, and what happens if you use the old value afterwards.",
    connections=[("previous", "Truthiness vs bool, if and match", "No truthiness: conditions are bool"),
                 ("next", "TypeScript unions vs enums", "Discriminated unions as enums")],
    recall=[
        dict(question="Why is the assignment rejected?",
             code=code(r'''
                 struct Counter { count: u32 }
                 impl Counter {
                     fn bump(&self) {
                         self.count += 1;
                     }
                 }
             '''),
             answer="`&self` is a shared reference, so the method may only read fields: E0594, cannot assign to `self.count`. Change the receiver to `&mut self`; callers then need a mutable binding.",
             expect={"errors": ["E0594"]}),
        dict(question="How does Rust express a JavaScript `static` method such as `Counter.fromText(text)`?",
             answer="As an associated function without a receiver in the `impl` block, for example `fn from_text(text: &str) -> Option<Counter>`, called as `Counter::from_text(\"3\")`. `new` is the same kind of function by convention, not a special constructor."),
    ],
    challenge=dict(
        function="new",
        starter=code(r'''
            // JavaScript original:
            // class Wallet {
            //   constructor() { this.cents = 0; }
            //   deposit(amount) { this.cents += amount; }
            //   withdraw(amount) {
            //     if (amount > this.cents) return false;
            //     this.cents -= amount;
            //     return true;
            //   }
            //   balance() { return this.cents; }
            //   close() { return this.cents; }  // the wallet must not be used afterwards
            // }
            pub struct Wallet {
                cents: u64,
            }

            impl Wallet {
                pub fn new() -> Wallet {
                    todo!("implement the contract")
                }

                pub fn deposit(&mut self, amount: u64) {
                    todo!("implement the contract")
                }

                pub fn withdraw(&mut self, amount: u64) -> bool {
                    todo!("implement the contract")
                }

                pub fn balance(&self) -> u64 {
                    todo!("implement the contract")
                }

                pub fn close(self) -> u64 {
                    todo!("implement the contract")
                }
            }
        '''),
        harness=code(r'''
            mod solution;

            use solution::Wallet;

            fn main() {
                let mut w = Wallet::new();
                assert_eq!(w.balance(), 0, "case 1");
                w.deposit(500);
                assert!(w.withdraw(200), "case 2");
                assert!(!w.withdraw(301), "case 3");
                assert_eq!(w.balance(), 300, "case 4");
                assert!(w.withdraw(300), "case 5");
                w.deposit(40);
                let reader = &w;
                assert_eq!(reader.balance(), 40, "case 6");
                assert_eq!(w.close(), 40, "case 7");

                println!("PASS node-objects-to-structs");
            }
        '''),
        cases=[
            ("visible", "Wallet::new().balance()", "0"),
            ("visible", "deposit(500), then withdraw(200)", "true"),
            ("semantic", "withdraw(301) with 300 left", "false"),
            ("boundary", "withdraw(300) with exactly 300 left", "true"),
            ("semantic", "balance() through a shared reference after deposit(40)", "40"),
            ("semantic", "close() consumes the wallet", "40"),
        ],
        required=["pub fn close(self)", "pub fn balance(&self)"],
        solution=code(r'''
            pub struct Wallet {
                cents: u64,
            }

            impl Wallet {
                pub fn new() -> Wallet {
                    Wallet { cents: 0 }
                }

                pub fn deposit(&mut self, amount: u64) {
                    self.cents += amount;
                }

                pub fn withdraw(&mut self, amount: u64) -> bool {
                    if amount > self.cents {
                        return false;
                    }
                    self.cents -= amount;
                    true
                }

                pub fn balance(&self) -> u64 {
                    self.cents
                }

                pub fn close(self) -> u64 {
                    self.cents
                }
            }
        '''),
        wrong=[
            ("refuses a withdrawal of the exact balance", code(r'''
                pub struct Wallet {
                    cents: u64,
                }

                impl Wallet {
                    pub fn new() -> Wallet {
                        Wallet { cents: 0 }
                    }

                    pub fn deposit(&mut self, amount: u64) {
                        self.cents += amount;
                    }

                    pub fn withdraw(&mut self, amount: u64) -> bool {
                        if amount >= self.cents {
                            return false;
                        }
                        self.cents -= amount;
                        true
                    }

                    pub fn balance(&self) -> u64 {
                        self.cents
                    }

                    pub fn close(self) -> u64 {
                        self.cents
                    }
                }
            ''')),
            ("balance takes &mut self, like a JavaScript method", code(r'''
                pub struct Wallet {
                    cents: u64,
                }

                impl Wallet {
                    pub fn new() -> Wallet {
                        Wallet { cents: 0 }
                    }

                    pub fn deposit(&mut self, amount: u64) {
                        self.cents += amount;
                    }

                    pub fn withdraw(&mut self, amount: u64) -> bool {
                        if amount > self.cents {
                            return false;
                        }
                        self.cents -= amount;
                        true
                    }

                    pub fn balance(&mut self) -> u64 {
                        self.cents
                    }

                    pub fn close(self) -> u64 {
                        self.cents
                    }
                }
            ''')),
        ],
        js_lang="javascript",
        js_original=code(r'''
            class Wallet {
              constructor() { this.cents = 0; }
              deposit(amount) { this.cents += amount; }
              withdraw(amount) {
                if (amount > this.cents) return false;
                this.cents -= amount;
                return true;
              }
              balance() { return this.cents; }
              close() { return this.cents; }
            }
            const w = new Wallet();
            const log = [w.balance()];
            w.deposit(500);
            log.push(w.withdraw(200), w.withdraw(301), w.balance(), w.withdraw(300));
            w.deposit(40);
            log.push(w.balance(), w.close());
        '''),
        js_checks=[("log", [0, True, False, 300, True, 40, 40])],
    ),
))

# ---------------------------------------------------------------- 7
LESSONS.append(dict(
    id="node-ts-unions-to-enums",
    unit="node-data",
    title="TypeScript unions vs enums",
    concept="Discriminated unions as enums",
    minutes=11,
    kind="runnable",
    summary="A TypeScript discriminated union becomes a Rust `enum` whose variants carry their own data, and `match` must handle every variant.",
    rule="An enum variant carries its own data, and `match` must cover every variant; a guard narrows an arm but never excuses a missing case.",
    explanation=[
        "A discriminated union is a set of object shapes sharing a tag such as `kind`, narrowed by a `switch`. Rust builds the same idea into the type system: `enum Payment { Card { last4: String }, Transfer { reference: String }, Cash }`. The variant is the tag. There is no string field to misspell, and data that belongs to one variant cannot be read through another.",
        "`match` replaces the `switch` plus the `never` trick. TypeScript checks exhaustiveness only if you add a `default` with `const unhandled: never`, and only at compile time: at runtime a value from JSON can still carry an unknown `kind`. Rust's `match` must cover every variant or the program does not compile (E0004), and a value of type `Payment` cannot hold anything else, because outside data has to be parsed into a variant first.",
        "Patterns destructure while they match. `Payment::Card { last4 } =>` binds the field, and a literal field such as `Shipped { days: 0, .. }` matches one specific value. A guard, `Payment::Cash if cents > 50_000 =>`, adds a condition; when it is false, matching continues with the next arm. Guards do not count toward exhaustiveness, so a plain `Payment::Cash =>` arm must still follow.",
        "Be careful with `_`. A wildcard arm silences E0004 for every variant added later, which is exactly the check you came for. In code that should be revisited whenever the enum grows, list the variants explicitly.",
    ],
    from_lang="typescript",
    from_label="TypeScript",
    from_code=code(r'''
        type Payment =
          | { kind: "card"; last4: string }
          | { kind: "transfer"; reference: string }
          | { kind: "cash" };

        function describe(p: Payment, cents: number): string {
          switch (p.kind) {
            case "card":
              return `card ending ${p.last4}`;
            case "transfer":
              return `transfer ${p.reference}`;
            case "cash":
              return cents > 50_000 ? "cash, needs approval" : "cash";
            default: {
              const unhandled: never = p; // compile error if a kind is added
              return unhandled;
            }
          }
        }

        console.log(describe({ kind: "card", last4: "4242" }, 900));
        console.log(describe({ kind: "cash" }, 60_000));
    '''),
    from_stdout="card ending 4242\ncash, needs approval\n",
    from_caption="A string tag narrows the union; the `never` default is TypeScript's opt-in exhaustiveness check.",
    example=code(r'''
        enum Payment {
            Card { last4: String },
            Transfer { reference: String },
            Cash,
        }

        fn describe(p: &Payment, cents: u32) -> String {
            match p {
                Payment::Card { last4 } => format!("card ending {last4}"),
                Payment::Transfer { reference } => format!("transfer {reference}"),
                Payment::Cash if cents > 50_000 => String::from("cash, needs approval"),
                Payment::Cash => String::from("cash"),
            }
        }

        fn main() {
            let card = Payment::Card { last4: String::from("4242") };
            let transfer = Payment::Transfer { reference: String::from("INV-7") };
            println!("{}", describe(&card, 900));
            println!("{}", describe(&Payment::Cash, 60_000));
            println!("{}", describe(&transfer, 100));
        }
    '''),
    example_stdout="card ending 4242\ncash, needs approval\ntransfer INV-7\n",
    example_caption="Each arm destructures its variant, and the guarded `Cash` arm is followed by an unguarded one.",
    contrasts=[
        ("`{ kind: \"card\"; last4: string }` uses a string tag.",
         "`Card { last4: String }`: the variant is the tag, and the compiler checks it."),
        ("Exhaustiveness needs `const unhandled: never = p` in `default`.",
         "Every `match` is checked; a missing variant is E0004."),
        ("JSON at runtime can carry any `kind` despite the type.",
         "A `Payment` can only be one of its variants; outside data must be parsed into one first."),
        ("`case \"cash\": return cents > 50_000 ? ... : ...`",
         "`Payment::Cash if cents > 50_000 =>` is a guard; a plain `Payment::Cash =>` arm must follow."),
    ],
    credits=["basics/enums", "basics/pattern-matching"],
    practice=code(r'''
        enum Payment {
            Card,
            Transfer,
            Cash,
        }

        fn fee(p: Payment) -> u32 {
            match p {
                Payment::Card => 30,
                Payment::Transfer => 0,
            }
        }

        fn main() {
            println!("{}", fee(Payment::Cash));
        }
    '''),
    practice_expect={"errors": ["E0004"], "messages": ["`Payment::Cash` not covered"]},
    question="A `match` on `Payment` ends with `_ => 0`. Later someone adds `Payment::Crypto`. What happens?",
    answers=[
        "rustc reports E0004 for the new variant",
        "The program panics when `Crypto` reaches the `match`",
        "It compiles, and `Crypto` silently takes the wildcard arm",
    ],
    correct=2,
    feedback="A wildcard covers every variant, including future ones, so the compiler has nothing to report. List the variants where a new one should force a review.",
    task="Port the TypeScript `eta` shown at the top of solution.rs; the `Shipment` enum is given. Return `not shipped yet`, `arrives today via <carrier>` for 0 days, `1 day via <carrier>`, `<n> days via <carrier>`, `delivered` and `lost`. Cover every variant without a `_` arm. In the Crabrix app, open the compiler lab and complete the supplied function in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every variant, including 0 and 1 days. Printing a success message alone does not complete this lab.",
    misconception="“A `_ =>` arm is the safe default, like `default:` in a `switch`.”",
    correction="A wildcard turns off the exhaustiveness check for every variant added later; in TypeScript terms it deletes the `never` check. List the variants unless the fallback is really meant for future cases too.",
    trace=[
        ("Read the variants", "`Card` and `Transfer` each carry a `String`, and `Cash` carries nothing. The amount is a separate parameter."),
        ("Order the arms", "The guarded `Payment::Cash if cents > 50_000` arm comes before the plain `Payment::Cash` arm. In the other order the guarded arm could never match, and rustc warns that it is unreachable."),
        ("Compare with evidence", "Run it: `card ending 4242`, `cash, needs approval`, `transfer INV-7`. Delete the plain `Cash` arm and read E0004: the guard does not cover `Cash`."),
    ],
    transfer="Add a `Voucher { code: String }` variant and compile before you touch `describe`. Then return `voucher <code>` for it, and use a guard to reject a voucher whose code is empty.",
    connections=[("previous", "Classes and objects vs structs", "Data in structs, behaviour in impl blocks"),
                 ("next", "null, undefined and ?? vs Option", "Absence as Option<T>")],
    recall=[
        dict(question="Why is this `match` rejected, even though both `Cash` amounts seem handled?",
             code=code(r'''
                 enum Payment { Card, Transfer, Cash }
                 let (p, cents) = (Payment::Cash, 40);
                 let fee = match p {
                     Payment::Card => 1,
                     Payment::Cash if cents > 100 => 2,
                     Payment::Cash if cents <= 100 => 3,
                 };
             '''),
             answer="The compiler does not reason about guard conditions, so `Cash` still counts as uncovered, and `Transfer` is missing as well: E0004. Make the last `Cash` arm unguarded and add a `Transfer` arm.",
             expect={"errors": ["E0004"]}),
        dict(question="In TypeScript, JSON with `kind: \"crypto\"` can reach a `switch` typed for three kinds. What happens instead in Rust?",
             answer="TypeScript types are erased, so the unknown `kind` reaches the `switch` at runtime and falls into the `never` branch. In Rust a `Payment` can only be built as one of its variants; parsing the JSON, for example with Serde, fails on the unknown tag before any `match` runs."),
    ],
    challenge=dict(
        function="eta",
        starter=code(r'''
            // TypeScript original:
            // type Shipment =
            //   | { status: "pending" }
            //   | { status: "shipped"; carrier: string; days: number }
            //   | { status: "delivered" }
            //   | { status: "lost" };
            // function eta(s: Shipment): string {
            //   switch (s.status) {
            //     case "pending": return "not shipped yet";
            //     case "shipped":
            //       if (s.days === 0) return `arrives today via ${s.carrier}`;
            //       return s.days === 1 ? `1 day via ${s.carrier}` : `${s.days} days via ${s.carrier}`;
            //     case "delivered": return "delivered";
            //     case "lost": return "lost";
            //   }
            // }
            pub enum Shipment {
                Pending,
                Shipped { carrier: String, days: u32 },
                Delivered,
                Lost,
            }

            pub fn eta(s: &Shipment) -> String {
                todo!("implement the contract")
            }
        '''),
        harness=code(r'''
            mod solution;

            use solution::Shipment;

            fn shipped(carrier: &str, days: u32) -> Shipment {
                Shipment::Shipped { carrier: carrier.to_string(), days }
            }

            fn main() {
                assert_eq!(solution::eta(&Shipment::Pending), "not shipped yet", "case 1");
                assert_eq!(solution::eta(&shipped("DHL", 0)), "arrives today via DHL", "case 2");
                assert_eq!(solution::eta(&shipped("UPS", 1)), "1 day via UPS", "case 3");
                assert_eq!(solution::eta(&shipped("DHL", 3)), "3 days via DHL", "case 4");
                assert_eq!(solution::eta(&Shipment::Delivered), "delivered", "case 5");
                assert_eq!(solution::eta(&Shipment::Lost), "lost", "case 6");

                println!("PASS node-ts-unions-to-enums");
            }
        '''),
        cases=[
            ("visible", "solution::eta(&Shipment::Pending)", "\"not shipped yet\""),
            ("boundary", "solution::eta(&Shipment::Shipped { carrier: \"DHL\".into(), days: 0 })", "\"arrives today via DHL\""),
            ("boundary", "solution::eta(&Shipment::Shipped { carrier: \"UPS\".into(), days: 1 })", "\"1 day via UPS\""),
            ("semantic", "solution::eta(&Shipment::Shipped { carrier: \"DHL\".into(), days: 3 })", "\"3 days via DHL\""),
            ("semantic", "solution::eta(&Shipment::Delivered)", "\"delivered\""),
            ("semantic", "solution::eta(&Shipment::Lost)", "\"lost\""),
        ],
        forbidden=["_ =>"],
        solution=code(r'''
            pub enum Shipment {
                Pending,
                Shipped { carrier: String, days: u32 },
                Delivered,
                Lost,
            }

            pub fn eta(s: &Shipment) -> String {
                match s {
                    Shipment::Pending => String::from("not shipped yet"),
                    Shipment::Shipped { carrier, days: 0 } => format!("arrives today via {carrier}"),
                    Shipment::Shipped { carrier, days: 1 } => format!("1 day via {carrier}"),
                    Shipment::Shipped { carrier, days } => format!("{days} days via {carrier}"),
                    Shipment::Delivered => String::from("delivered"),
                    Shipment::Lost => String::from("lost"),
                }
            }
        '''),
        wrong=[
            ("general Shipped arm placed first", code(r'''
                pub enum Shipment {
                    Pending,
                    Shipped { carrier: String, days: u32 },
                    Delivered,
                    Lost,
                }

                pub fn eta(s: &Shipment) -> String {
                    match s {
                        Shipment::Pending => String::from("not shipped yet"),
                        Shipment::Shipped { carrier, days } => format!("{days} days via {carrier}"),
                        Shipment::Shipped { carrier, days: 0 } => format!("arrives today via {carrier}"),
                        Shipment::Shipped { carrier, days: 1 } => format!("1 day via {carrier}"),
                        Shipment::Delivered => String::from("delivered"),
                        Shipment::Lost => String::from("lost"),
                    }
                }
            ''')),
            ("switch-style default arm swallows Lost", code(r'''
                pub enum Shipment {
                    Pending,
                    Shipped { carrier: String, days: u32 },
                    Delivered,
                    Lost,
                }

                pub fn eta(s: &Shipment) -> String {
                    match s {
                        Shipment::Pending => String::from("not shipped yet"),
                        Shipment::Shipped { carrier, days: 0 } => format!("arrives today via {carrier}"),
                        Shipment::Shipped { carrier, days: 1 } => format!("1 day via {carrier}"),
                        Shipment::Shipped { carrier, days } => format!("{days} days via {carrier}"),
                        _ => String::from("delivered"),
                    }
                }
            ''')),
            ("forgets the Lost variant", code(r'''
                pub enum Shipment {
                    Pending,
                    Shipped { carrier: String, days: u32 },
                    Delivered,
                    Lost,
                }

                pub fn eta(s: &Shipment) -> String {
                    match s {
                        Shipment::Pending => String::from("not shipped yet"),
                        Shipment::Shipped { carrier, days: 0 } => format!("arrives today via {carrier}"),
                        Shipment::Shipped { carrier, days: 1 } => format!("1 day via {carrier}"),
                        Shipment::Shipped { carrier, days } => format!("{days} days via {carrier}"),
                        Shipment::Delivered => String::from("delivered"),
                    }
                }
            ''')),
        ],
        js_lang="typescript",
        js_original=code(r'''
            type Shipment =
              | { status: "pending" }
              | { status: "shipped"; carrier: string; days: number }
              | { status: "delivered" }
              | { status: "lost" };
            function eta(s: Shipment): string {
              switch (s.status) {
                case "pending": return "not shipped yet";
                case "shipped":
                  if (s.days === 0) return `arrives today via ${s.carrier}`;
                  return s.days === 1 ? `1 day via ${s.carrier}` : `${s.days} days via ${s.carrier}`;
                case "delivered": return "delivered";
                case "lost": return "lost";
              }
            }
        '''),
        js_checks=[("eta({ status: \"pending\" })", "not shipped yet"),
                   ("eta({ status: \"shipped\", carrier: \"DHL\", days: 0 })", "arrives today via DHL"),
                   ("eta({ status: \"shipped\", carrier: \"UPS\", days: 1 })", "1 day via UPS"),
                   ("eta({ status: \"shipped\", carrier: \"DHL\", days: 3 })", "3 days via DHL"),
                   ("eta({ status: \"delivered\" })", "delivered"), ("eta({ status: \"lost\" })", "lost")],
    ),
))

# ---------------------------------------------------------------- 8
LESSONS.append(dict(
    id="node-null-undefined-to-option",
    unit="node-data",
    title="null, undefined and ?? vs Option",
    concept="Absence as Option<T>",
    minutes=11,
    kind="runnable",
    summary="`null` and `undefined` become `Option<T>`: absence is part of the type, and `?.` and `??` become `and_then`, `map` and `unwrap_or`.",
    rule="Use `Option<T>` when a value may be absent and `Result<T, E>` when the caller needs the reason; `unwrap_or` replaces `??`, not `||`.",
    explanation=[
        "TypeScript with `strictNullChecks` already marks absence as `T | undefined`, but the value can still be `null`, `undefined` or a missing property, and the checks vanish at runtime. Rust has no null. A value that may be missing has type `Option<T>`, which is either `Some(value)` or `None`, and you cannot use it as a `T` until you decide what absence means. `network.retries + 1` with an `Option<u32>` is a compile error, not `NaN`.",
        "The operators become methods. `a?.b` is `a.as_ref().and_then(|a| a.b)` when `b` is itself optional, and `.map(...)` when it is not. `x ?? 3` is `x.unwrap_or(3)`, or `unwrap_or_else(|| ...)` when the default is expensive to build. Inside a function that returns `Option`, `let n = config.network.as_ref()?;` returns `None` early, the closest thing to optional chaining across statements.",
        "There is no `||` default. `retries || 3` turns a configured `0` into `3`, and `title || \"Untitled\"` discards an intentionally empty string. `unwrap_or` only replaces `None`, so `Some(0)` stays `0`. If zero really should count as missing, say so with `.filter(|&n| n != 0)` and a comment.",
        "`Option` answers whether something is there; it does not say why not. When the caller needs a reason, such as \"storage unreachable\" rather than \"no such user\", return `Result<T, E>`, or `Result<Option<T>, E>` when missing is a normal outcome and failure is a separate one. That replaces returning `null` from one path and throwing from another.",
    ],
    from_lang="typescript",
    from_label="TypeScript",
    from_code=code(r'''
        interface Config {
          network?: { retries?: number };
        }

        function retryLimit(config: Config): number {
          return config.network?.retries ?? 3;
        }

        function retryLimitBuggy(config: Config): number {
          return config.network?.retries || 3; // 0 is falsy
        }

        console.log(retryLimit({}), retryLimit({ network: { retries: 0 } }));
        console.log(retryLimitBuggy({ network: { retries: 0 } }));
    '''),
    from_stdout="3 0\n3\n",
    from_caption="`?.` and `??` keep a configured `0`, while `||` replaces it with the default.",
    example=code(r'''
        struct Network {
            retries: Option<u32>,
        }

        struct Config {
            network: Option<Network>,
        }

        fn retry_limit(config: &Config) -> u32 {
            config.network.as_ref().and_then(|n| n.retries).unwrap_or(3)
        }

        fn main() {
            let empty = Config { network: None };
            let zero = Config { network: Some(Network { retries: Some(0) }) };
            println!("{} {}", retry_limit(&empty), retry_limit(&zero));
        }
    '''),
    example_stdout="3 0\n",
    example_caption="`and_then` follows the optional chain and `unwrap_or` supplies the `??` default, so `Some(0)` stays `0`.",
    contrasts=[
        ("`retries?: number` may be missing, `undefined` or `null`.",
         "`retries: Option<u32>` is `Some(n)` or `None`, and must be handled before use."),
        ("`config.network?.retries ?? 3`",
         "`config.network.as_ref().and_then(|n| n.retries).unwrap_or(3)`"),
        ("`retries || 3` turns a configured `0` into `3`.",
         "`unwrap_or(3)` replaces only `None`; `Some(0)` stays `0`."),
        ("`undefined + 1` is `NaN` at runtime.",
         "Adding an integer to an `Option<u32>` is E0369 at compile time."),
    ],
    credits=["basics/option-result"],
    practice=code(r'''
        struct Network {
            retries: Option<u32>,
        }

        fn main() {
            let network = Network { retries: Some(0) };
            let limit: u32 = network.retries + 1;
            println!("{limit}");
        }
    '''),
    practice_expect={"errors": ["E0369"]},
    question="A lookup finds nothing when the key is missing, and fails when the storage is unreachable. Which return type gives the caller both facts?",
    answers=[
        "`Option<T>`",
        "`Result<Option<T>, E>`",
        "`T`, using `null` for both cases",
    ],
    correct=1,
    feedback="`Ok(Some(t))` means found, `Ok(None)` simply missing, and `Err(e)` carries the reason the lookup itself failed.",
    task="Port the TypeScript `pageSize` and `title` shown at the top of solution.rs. Both take `Option<&Settings>`. A missing settings value or field uses the default (20, `Untitled`), but a configured `0` or an empty title is kept, exactly as `??` does. In the Crabrix app, open the compiler lab and complete the supplied functions in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including a configured `0` and an empty title. Printing a success message alone does not complete this lab.",
    misconception="“`unwrap_or` is Rust's `||`: it replaces any empty-looking value.”",
    correction="`unwrap_or` replaces only `None`, like `??`. `Some(0)` and `Some(String::new())` are present values and are returned unchanged.",
    trace=[
        ("Read the types", "`Config.network` is an `Option<Network>` and `Network.retries` an `Option<u32>`: two separate places where data may be missing."),
        ("Follow the chain", "`as_ref()` borrows the network instead of moving it out of `config`. `and_then(|n| n.retries)` flattens the two options, and `unwrap_or(3)` handles both kinds of `None`."),
        ("Compare with evidence", "Run it: `3 0`, so the configured zero survives. Insert `.filter(|&n| n != 0)` before `unwrap_or` and the second number becomes `3`, the `||` behaviour."),
    ],
    transfer="Write `fn retries(config: &Config) -> Option<u32>` using `?` on `config.network.as_ref()` instead of `and_then`. Then change the return type to `Result<u32, String>` and use `ok_or` to say which field was missing.",
    connections=[("previous", "TypeScript unions vs enums", "Discriminated unions as enums"),
                 ("next", "Array methods vs iterators", "Lazy iterator pipelines")],
    recall=[
        dict(question="What does each line print?",
             code=code(r'''
                 let a: Option<u32> = Some(0);
                 let b: Option<u32> = None;
                 println!("{}", a.unwrap_or(5));
                 println!("{}", b.unwrap_or(5));
                 println!("{:?}", a.map(|n| n + 1));
             '''),
             answer="`0`, then `5`, then `Some(1)`. `unwrap_or` replaces only `None`, like `??`, so the present zero is kept. `map` transforms the value inside `Some` and would leave a `None` as `None`.",
             expect={"stdout": "0\n5\nSome(1)\n"}),
        dict(question="Why is this rejected when `config` is a `&Config`, and what fixes it?",
             code=code(r'''
                 struct Network { retries: Option<u32> }
                 struct Config { network: Option<Network> }
                 fn retry_limit(config: &Config) -> u32 {
                     config.network.and_then(|n| n.retries).unwrap_or(3)
                 }
             '''),
             answer="`and_then` takes the `Option` by value, which would move `network` out of a struct you only borrowed: E0507. Call `config.network.as_ref()` first to get an `Option<&Network>`; then `n.retries` copies the `Option<u32>` out through the reference.",
             expect={"errors": ["E0507"]}),
    ],
    challenge=dict(
        function="page_size",
        starter=code(r'''
            // TypeScript original:
            // interface Settings { pageSize?: number; title?: string }
            // function pageSize(s?: Settings): number {
            //   return s?.pageSize ?? 20;
            // }
            // function title(s?: Settings): string {
            //   return s?.title ?? "Untitled";
            // }
            pub struct Settings {
                pub page_size: Option<u32>,
                pub title: Option<String>,
            }

            pub fn page_size(s: Option<&Settings>) -> u32 {
                todo!("implement the contract")
            }

            pub fn title(s: Option<&Settings>) -> String {
                todo!("implement the contract")
            }
        '''),
        harness=code(r'''
            mod solution;

            use solution::Settings;

            fn settings(page_size: Option<u32>, title: Option<&str>) -> Settings {
                Settings { page_size, title: title.map(String::from) }
            }

            fn main() {
                assert_eq!(solution::page_size(None), 20, "case 1");
                assert_eq!(solution::page_size(Some(&settings(None, None))), 20, "case 2");
                assert_eq!(solution::page_size(Some(&settings(Some(0), None))), 0, "case 3");
                assert_eq!(solution::page_size(Some(&settings(Some(50), None))), 50, "case 4");
                assert_eq!(solution::title(None), "Untitled", "case 5");
                assert_eq!(solution::title(Some(&settings(None, Some("")))), "", "case 6");
                assert_eq!(solution::title(Some(&settings(None, Some("Q4")))), "Q4", "case 7");
                let kept = settings(Some(5), Some("kept"));
                solution::title(Some(&kept));
                assert_eq!(kept.title.as_deref(), Some("kept"), "case 8");

                println!("PASS node-null-undefined-to-option");
            }
        '''),
        cases=[
            ("visible", "solution::page_size(None)", "20"),
            ("semantic", "page_size of settings without pageSize", "20"),
            ("boundary", "page_size of settings with Some(0)", "0"),
            ("semantic", "page_size of settings with Some(50)", "50"),
            ("visible", "solution::title(None)", "\"Untitled\""),
            ("boundary", "title of settings with Some(\"\")", "\"\""),
            ("semantic", "title of settings with Some(\"Q4\")", "\"Q4\""),
        ],
        required=["pub fn title"],
        solution=code(r'''
            pub struct Settings {
                pub page_size: Option<u32>,
                pub title: Option<String>,
            }

            pub fn page_size(s: Option<&Settings>) -> u32 {
                s.and_then(|s| s.page_size).unwrap_or(20)
            }

            pub fn title(s: Option<&Settings>) -> String {
                s.and_then(|s| s.title.clone()).unwrap_or_else(|| String::from("Untitled"))
            }
        '''),
        wrong=[
            ("ports || instead of ??: zero and empty count as missing", code(r'''
                pub struct Settings {
                    pub page_size: Option<u32>,
                    pub title: Option<String>,
                }

                pub fn page_size(s: Option<&Settings>) -> u32 {
                    s.and_then(|s| s.page_size).filter(|&n| n != 0).unwrap_or(20)
                }

                pub fn title(s: Option<&Settings>) -> String {
                    s.and_then(|s| s.title.clone())
                        .filter(|t| !t.is_empty())
                        .unwrap_or_else(|| String::from("Untitled"))
                }
            ''')),
            ("moves the title out of borrowed settings", code(r'''
                pub struct Settings {
                    pub page_size: Option<u32>,
                    pub title: Option<String>,
                }

                pub fn page_size(s: Option<&Settings>) -> u32 {
                    s.and_then(|s| s.page_size).unwrap_or(20)
                }

                pub fn title(s: Option<&Settings>) -> String {
                    s.and_then(|s| s.title).unwrap_or_else(|| String::from("Untitled"))
                }
            ''')),
        ],
        js_lang="typescript",
        js_original=code(r'''
            interface Settings { pageSize?: number; title?: string }
            function pageSize(s?: Settings): number {
              return s?.pageSize ?? 20;
            }
            function title(s?: Settings): string {
              return s?.title ?? "Untitled";
            }
        '''),
        js_checks=[("pageSize()", 20), ("pageSize({})", 20), ("pageSize({ pageSize: 0 })", 0),
                   ("pageSize({ pageSize: 50 })", 50), ("title()", "Untitled"), ("title({ title: \"\" })", ""),
                   ("title({ title: \"Q4\" })", "Q4")],
    ),
))

# ---------------------------------------------------------------- 9
LESSONS.append(dict(
    id="node-array-methods-to-iterators",
    unit="node-data",
    title="Array methods vs iterators",
    concept="Lazy iterator pipelines",
    minutes=12,
    kind="runnable",
    summary="`map` and `filter` on an array run at once and build new arrays; Rust's iterator adapters do nothing until a consumer such as `sum`, `find` or `collect` pulls values.",
    rule="Iterator adapters are lazy: a consumer such as `sum`, `find`, `collect` or a `for` loop drives the work, one item at a time.",
    explanation=[
        "`orders.filter(...).map(...).reduce(...)` runs each stage over the whole array and allocates an intermediate array between stages. Rust's `orders.iter().filter(...).map(...).sum()` first builds a description of the work. Nothing happens until `sum` asks for the first item; then each order flows through `filter` and `map` one at a time, with no intermediate `Vec`.",
        "Laziness changes what runs. In the JavaScript example, `map(...).find(...)` calls the mapping function for all three orders before `find` looks at one. The Rust pipeline stops at the first match, so its closure runs once. A pipeline that is never consumed does nothing at all, which is why rustc warns that an unused `Map` must be used in the practice code.",
        "The names mostly carry over: `map`, `filter` and `find` are the same, `some` is `any`, `every` is `all`, `reduce` with an initial value is `fold`, and `flatMap` is `flat_map`. The length of a filtered result is `count()`, and `collect::<Vec<_>>()` gives you a collection back. There is no index argument; add `.enumerate()` to get `(index, item)` pairs.",
        "Watch what the iterator yields. `iter()` yields references (`&Order`), `iter_mut()` yields `&mut Order`, and `into_iter()` on a `Vec` yields owned values and consumes the vector. That is why the closures read `o.cents` through a reference, and why `find(|&c| c > 1000)` destructures the `&u64` it receives.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        const orders = [
          { cents: 1200, paid: true },
          { cents: 300, paid: false },
          { cents: 450, paid: true },
        ];

        let calls = 0;
        const paidTotal = orders
          .filter((o) => o.paid)
          .map((o) => { calls += 1; return o.cents; }) // runs now, builds an array
          .reduce((sum, c) => sum + c, 0);
        console.log(paidTotal, calls);

        const firstBig = orders.map((o) => { calls += 1; return o.cents; }).find((c) => c > 1000);
        console.log(firstBig, calls); // map ran for all three orders
    '''),
    from_stdout="1650 2\n1200 5\n",
    from_caption="`map` runs eagerly, so the search for the first big order still maps all three orders.",
    example=code(r'''
        struct Order {
            cents: u64,
            paid: bool,
        }

        fn main() {
            let orders = [
                Order { cents: 1200, paid: true },
                Order { cents: 300, paid: false },
                Order { cents: 450, paid: true },
            ];
            let mut calls = 0;
            let paid_total: u64 = orders
                .iter()
                .filter(|o| o.paid)
                .map(|o| { calls += 1; o.cents })
                .sum();
            println!("{paid_total} {calls}");

            let first_big = orders.iter().map(|o| { calls += 1; o.cents }).find(|&c| c > 1000);
            println!("{first_big:?} {calls}");
        }
    '''),
    example_stdout="1650 2\nSome(1200) 3\n",
    example_caption="The closure counter shows the difference: two calls for the total, and the search stops after one more.",
    contrasts=[
        ("Each array method runs immediately over every element.",
         "Adapters such as `map` and `filter` run only when a consumer pulls items."),
        ("`arr.map(f).find(p)` calls `f` for every element.",
         "`iter.map(f).find(p)` stops calling `f` after the first match."),
        ("Each stage allocates a new array.",
         "No intermediate collection is built unless you call `collect`."),
        ("`reduce((s, x) => s + x, 0)`",
         "`sum()`, or `fold(0, |s, x| s + x)` for a general accumulator."),
    ],
    credits=["ownership/iterators", "ownership/iterator-adapters"],
    practice=code(r'''
        fn main() {
            let prices = vec![3, 7, 12];
            prices.iter().map(|p| {
                println!("checking {p}");
                p * 2
            });
            println!("done");
        }
    '''),
    practice_expect={"stdout": "done\n", "warnings": ["unused `Map` that must be used"]},
    question="In the practice code, what has `map` done by the time `done` prints?",
    answers=[
        "Nothing: no consumer such as `sum`, `collect` or `for` asked for a value",
        "It doubled all three prices into a new vector, like `Array.prototype.map`",
        "It doubled the first price and then paused",
    ],
    correct=0,
    feedback="An adapter only describes work. Without a consumer the closure never runs, and rustc warns that the `Map` must be used.",
    task="Port the JavaScript `firstPriceOver` shown at the top of solution.rs, but keep the Rust version lazy: call `price_of` only until the first price above `limit` is found. The harness counts the calls. In the Crabrix app, open the compiler lab and complete the supplied function in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including the number of `price_of` calls and an empty slice. Printing a success message alone does not complete this lab.",
    misconception="“`iter().map(...)` works like `Array.prototype.map`: it builds the new values right away.”",
    correction="`map` returns a lazy adapter. The closure runs only when a consumer pulls an item, and only for the items it pulls.",
    trace=[
        ("Read the pipeline", "`orders.iter()` yields `&Order`. `filter` keeps the paid orders, `map` turns each into its cents, and `sum` is the only consumer."),
        ("Count the work", "`sum` pulls items one at a time. Only the two paid orders reach `map`, so `calls` becomes 2; the unpaid order never does."),
        ("Compare with evidence", "Run it: `1650 2`, then `Some(1200) 3`. `find` stopped after the first order, while JavaScript's `map` had already run for all three."),
    ],
    transfer="Insert `.inspect(|o| println!(\"saw {}\", o.cents))` right after `orders.iter()` in both pipelines and predict the printed lines. Then add `.collect::<Vec<_>>()` after the second `map`, iterate that vector for the `find`, and count the calls again.",
    connections=[("previous", "null, undefined and ?? vs Option", "Absence as Option<T>"),
                 ("next", "Objects and Map vs HashMap", "Keyed data with HashMap and entry")],
    recall=[
        dict(question="What does this print, and why not three `map` lines?",
             code=code(r'''
                 let v = [1, 2, 3];
                 let first = v.iter()
                     .map(|x| { println!("map {x}"); x * 10 })
                     .find(|x| x % 20 == 0);
                 println!("{first:?}");
             '''),
             answer="`map 1`, `map 2`, then `Some(20)`. `find` pulls one item at a time and stops at the first match, so the closure never runs for `3`. An array's `map` would have logged all three before searching.",
             expect={"stdout": "map 1\nmap 2\nSome(20)\n"}),
        dict(question="What are the Rust names for `some`, `every`, `reduce` with an initial value, and `flatMap`?",
             answer="`any`, `all`, `fold(initial, |acc, x| ...)` and `flat_map`. As in JavaScript, `any` and `all` short-circuit. Unlike the array methods, they work on any iterator, and the adapters before them run lazily."),
    ],
    challenge=dict(
        function="first_price_over",
        starter=code(r'''
            // JavaScript original:
            // function firstPriceOver(items, limit, priceOf) {
            //   return items.map(priceOf).find((p) => p > limit);
            // }
            // Array.prototype.map calls priceOf for every item before find runs.
            // Keep the Rust version lazy: stop calling price_of after the first match.
            pub fn first_price_over(items: &[u32], limit: u32, price_of: impl FnMut(u32) -> u32) -> Option<u32> {
                todo!("implement the contract")
            }
        '''),
        harness=code(r'''
            mod solution;

            fn main() {
                let mut calls = 0;
                let found = solution::first_price_over(&[1, 5, 9, 12], 6, |x| { calls += 1; x });
                assert_eq!((found, calls), (Some(9), 3), "case 1");

                let mut calls = 0;
                let found = solution::first_price_over(&[], 6, |x| { calls += 1; x });
                assert_eq!((found, calls), (None, 0), "case 2");

                let mut calls = 0;
                let found = solution::first_price_over(&[2, 6, 4], 6, |x| { calls += 1; x });
                assert_eq!((found, calls), (None, 3), "case 3");

                let mut calls = 0;
                let found = solution::first_price_over(&[3, 7, 100], 10, |x| { calls += 1; x * 2 });
                assert_eq!((found, calls), (Some(14), 2), "case 4");

                println!("PASS node-array-methods-to-iterators");
            }
        '''),
        cases=[
            ("visible", "first_price_over(&[1, 5, 9, 12], 6, identity): result and calls", "(Some(9), 3)"),
            ("boundary", "first_price_over(&[], 6, identity): result and calls", "(None, 0)"),
            ("boundary", "first_price_over(&[2, 6, 4], 6, identity): a price equal to the limit is not over it", "(None, 3)"),
            ("semantic", "first_price_over(&[3, 7, 100], 10, double): result and calls", "(Some(14), 2)"),
        ],
        solution=code(r'''
            pub fn first_price_over(items: &[u32], limit: u32, price_of: impl FnMut(u32) -> u32) -> Option<u32> {
                items.iter().copied().map(price_of).find(|&price| price > limit)
            }
        '''),
        wrong=[
            ("collects every price first, like Array.prototype.map", code(r'''
                pub fn first_price_over(items: &[u32], limit: u32, mut price_of: impl FnMut(u32) -> u32) -> Option<u32> {
                    let prices: Vec<u32> = items.iter().map(|&item| price_of(item)).collect();
                    prices.into_iter().find(|&price| price > limit)
                }
            ''')),
            ("uses >= instead of >", code(r'''
                pub fn first_price_over(items: &[u32], limit: u32, price_of: impl FnMut(u32) -> u32) -> Option<u32> {
                    items.iter().copied().map(price_of).find(|&price| price >= limit)
                }
            ''')),
        ],
        js_lang="javascript",
        js_original=code(r'''
            function firstPriceOver(items, limit, priceOf) {
              return items.map(priceOf).find((p) => p > limit);
            }
            function counted(items, limit, f) {
              let calls = 0;
              const found = firstPriceOver(items, limit, (x) => { calls += 1; return f(x); });
              return [found ?? null, calls];
            }
        '''),
        js_checks=[("counted([1, 5, 9, 12], 6, (x) => x)", [9, 4]), ("counted([], 6, (x) => x)", [None, 0]),
                   ("counted([2, 6, 4], 6, (x) => x)", [None, 3]), ("counted([3, 7, 100], 10, (x) => x * 2)", [14, 3])],
    ),
))

# ---------------------------------------------------------------- 10
LESSONS.append(dict(
    id="node-map-and-objects-to-hashmap",
    unit="node-data",
    title="Objects and Map vs HashMap",
    concept="Keyed data with HashMap and entry",
    minutes=11,
    kind="runnable",
    summary="Plain objects used as dictionaries become `HashMap<K, V>`: typed keys, no prototype keys, and `entry` for update-or-insert in one lookup.",
    rule="`entry(key).or_insert(default)` looks the key up once and returns a mutable reference to the value, whether or not it was already there.",
    explanation=[
        "Objects make convenient dictionaries until a key collides with the prototype. In the JavaScript example, `counts[\"constructor\"]` finds `Object.prototype.constructor`, so `(counts[word] || 0) + 1` produces `\"function Object() { [native code] }1\"`. Keys are also converted to strings, so `1` and `\"1\"` are the same key. `Map` fixes both problems, and `HashMap<K, V>` is its Rust counterpart: keys and values have declared types, and only inserted keys exist.",
        "The counting idiom becomes the `entry` API. `counts.entry(word)` looks the key up once and returns an `Entry`; `or_insert(0)` inserts the default if the slot was vacant and returns `&mut u32` in both cases, so `*... += 1` updates in place. `get` followed by `insert` does two lookups, and `insert` alone overwrites like `Map.set`, which is the classic bug when porting `totals.set(k, (totals.get(k) ?? 0) + v)`.",
        "Reading is explicit about absence. `counts.get(\"be\")` returns an `Option<&u32>`. `counts[\"be\"]` also compiles, but it panics when the key is missing instead of returning `undefined`, so use indexing only for keys you know are present.",
        "Iteration order is not insertion order. A `Map` preserves insertion order; a `HashMap` uses a randomly seeded hasher, so its order can differ between runs. Sort the keys, or use a `BTreeMap` for key order, when output must be stable. Splitting text differs too: `split(' ')` keeps the empty strings between double spaces in both languages, while `split_whitespace()` skips them.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        function countWords(text) {
          const counts = {};
          for (const word of text.split(" ")) {
            counts[word] = (counts[word] || 0) + 1;
          }
          return counts;
        }

        console.log(countWords("to be or not to be"));
        console.log(countWords("a  b"));        // "" became a key
        console.log(countWords("constructor")); // inherited from Object.prototype
    '''),
    from_stdout="{ to: 2, be: 2, or: 1, not: 1 }\n{ a: 1, '': 1, b: 1 }\n{ constructor: 'function Object() { [native code] }1' }\n",
    from_caption="An object used as a dictionary: `\"\"` becomes a key, and `constructor` collides with `Object.prototype`.",
    example=code(r'''
        use std::collections::HashMap;

        fn count_words(text: &str) -> HashMap<&str, u32> {
            let mut counts = HashMap::new();
            for word in text.split_whitespace() {
                *counts.entry(word).or_insert(0) += 1;
            }
            counts
        }

        fn main() {
            let counts = count_words("to be or not to be");
            println!("{} {}", counts["to"], counts.get("not").copied().unwrap_or(0));
            println!("{:?}", count_words("a  b").get(""));
            println!("{:?}", count_words("constructor"));
        }
    '''),
    example_stdout="2 1\nNone\n{\"constructor\": 1}\n",
    example_caption="`split_whitespace` drops empty words, `entry` updates in one lookup, and `constructor` is just another key.",
    contrasts=[
        ("Object keys are strings, and `\"constructor\"` already exists on the prototype.",
         "A `HashMap<&str, u32>` contains only inserted keys, all of one declared type."),
        ("`map.set(k, (map.get(k) ?? 0) + 1)` looks the key up twice.",
         "`*map.entry(k).or_insert(0) += 1` looks it up once and updates in place."),
        ("A missing key reads as `undefined`.",
         "`get` returns `None`; `map[key]` panics when the key is missing."),
        ("`Map` iterates in insertion order.",
         "`HashMap` order is unspecified; use a `BTreeMap` or sort the keys for stable output."),
    ],
    credits=["basics/collections"],
    practice=code(r'''
        use std::collections::HashMap;

        fn main() {
            let mut counts: HashMap<&str, u32> = HashMap::new();
            counts.insert("to", 2);
            let be = counts["be"];
            println!("{be}");
        }
    '''),
    practice_expect={"panic": "panicked at"},
    question="Why is `*counts.entry(word).or_insert(0) += 1` preferred over `get` followed by `insert`?",
    answers=[
        "It keeps the keys sorted",
        "It avoids allocating the key",
        "It looks the key up once and returns a mutable reference whether or not the entry existed",
    ],
    correct=2,
    feedback="`or_insert` returns `&mut V` for both the vacant and the occupied case, so one lookup covers the update.",
    task="Port the JavaScript `totalsByCustomer` shown at the top of solution.rs. Add each order's cents to its customer's total, using `entry` for the update, and return the map. Keys are case-sensitive. In the Crabrix app, open the compiler lab and complete the supplied function in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including repeated customers, an empty list and a `constructor` key. Printing a success message alone does not complete this lab.",
    misconception="“`insert` adds to the existing value, the way the JavaScript counting line does.”",
    correction="`insert` replaces the old value and returns it as an `Option<V>`, like `Map.set`. Use `entry(key).or_insert(0)` and add through the returned `&mut V`.",
    trace=[
        ("Read the key type", "`count_words` returns `HashMap<&str, u32>`: the keys borrow slices of `text`, so no `String` is allocated per word."),
        ("Follow one update", "For the second `\"to\"`, `entry` finds the occupied slot, `or_insert(0)` returns a `&mut u32` holding 1, and `+= 1` makes it 2."),
        ("Compare with evidence", "Run it: `2 1`, `None` for the empty key, and `{\"constructor\": 1}`. Replace `split_whitespace()` with `split(' ')` and `get(\"\")` returns `Some(1)` for `\"a  b\"`."),
    ],
    transfer="Make `count_words` return a `BTreeMap` and print the whole map for `\"to be or not to be\"`. Then explain why the `HashMap` version might print the same pairs in a different order on another run.",
    connections=[("previous", "Array methods vs iterators", "Lazy iterator pipelines"),
                 ("next", "UTF-16 strings vs UTF-8 String", "UTF-8 bytes, chars and lengths")],
    recall=[
        dict(question="What does this print?",
             code=code(r'''
                 use std::collections::HashMap;
                 let mut m = HashMap::new();
                 m.insert("ana", 5);
                 let old = m.insert("ana", 2);
                 println!("{:?} {:?}", old, m.get("ana"));
             '''),
             answer="`Some(5) Some(2)`. `insert` replaces the value, like `Map.set`, and returns the previous one. To add instead, write `*m.entry(\"ana\").or_insert(0) += 2`.",
             expect={"stdout": "Some(5) Some(2)\n"}),
        dict(question="Why might two runs of the same program print a `HashMap` in different orders, and what are two fixes?",
             answer="`HashMap` uses a randomly seeded hasher to resist collision attacks, and its iteration order is unspecified. Collect the keys into a `Vec` and sort them, or use a `BTreeMap`, which iterates in key order. Insertion order, which a JavaScript `Map` keeps, is promised by neither type."),
    ],
    challenge=dict(
        function="totals_by_customer",
        starter=code(r'''
            // JavaScript original:
            // function totalsByCustomer(orders) {
            //   const totals = new Map();
            //   for (const [customer, cents] of orders) {
            //     totals.set(customer, (totals.get(customer) ?? 0) + cents);
            //   }
            //   return totals;
            // }
            use std::collections::HashMap;

            pub fn totals_by_customer(orders: &[(&str, u64)]) -> HashMap<String, u64> {
                todo!("implement the contract")
            }
        '''),
        harness=code(r'''
            mod solution;

            use std::collections::HashMap;

            fn map(pairs: &[(&str, u64)]) -> HashMap<String, u64> {
                pairs.iter().map(|&(name, cents)| (name.to_string(), cents)).collect()
            }

            fn main() {
                let orders = [("ana", 500), ("bo", 200), ("ana", 250)];
                assert_eq!(solution::totals_by_customer(&orders), map(&[("ana", 750), ("bo", 200)]), "case 1");
                assert_eq!(solution::totals_by_customer(&[]), map(&[]), "case 2");
                let tricky = [("constructor", 1), ("constructor", 2)];
                assert_eq!(solution::totals_by_customer(&tricky), map(&[("constructor", 3)]), "case 3");
                let cased = [("Ana", 1), ("ana", 2)];
                assert_eq!(solution::totals_by_customer(&cased), map(&[("Ana", 1), ("ana", 2)]), "case 4");

                println!("PASS node-map-and-objects-to-hashmap");
            }
        '''),
        cases=[
            ("visible", "totals_by_customer(&[(\"ana\", 500), (\"bo\", 200), (\"ana\", 250)])", "{ana: 750, bo: 200}"),
            ("boundary", "totals_by_customer(&[])", "{}"),
            ("semantic", "totals_by_customer(&[(\"constructor\", 1), (\"constructor\", 2)])", "{constructor: 3}"),
            ("semantic", "totals_by_customer(&[(\"Ana\", 1), (\"ana\", 2)])", "{Ana: 1, ana: 2}"),
        ],
        required=[".entry("],
        solution=code(r'''
            use std::collections::HashMap;

            pub fn totals_by_customer(orders: &[(&str, u64)]) -> HashMap<String, u64> {
                let mut totals = HashMap::new();
                for &(customer, cents) in orders {
                    *totals.entry(customer.to_string()).or_insert(0) += cents;
                }
                totals
            }
        '''),
        wrong=[
            ("ports Map.set as insert and overwrites the total", code(r'''
                use std::collections::HashMap;

                pub fn totals_by_customer(orders: &[(&str, u64)]) -> HashMap<String, u64> {
                    let mut totals = HashMap::new();
                    for &(customer, cents) in orders {
                        totals.entry(customer.to_string()).or_insert(0);
                        totals.insert(customer.to_string(), cents);
                    }
                    totals
                }
            ''')),
            ("get then insert instead of entry", code(r'''
                use std::collections::HashMap;

                pub fn totals_by_customer(orders: &[(&str, u64)]) -> HashMap<String, u64> {
                    let mut totals: HashMap<String, u64> = HashMap::new();
                    for &(customer, cents) in orders {
                        let current = totals.get(customer).copied().unwrap_or(0);
                        totals.insert(customer.to_string(), current + cents);
                    }
                    totals
                }
            ''')),
        ],
        js_lang="javascript",
        js_original=code(r'''
            function totalsByCustomer(orders) {
              const totals = new Map();
              for (const [customer, cents] of orders) {
                totals.set(customer, (totals.get(customer) ?? 0) + cents);
              }
              return totals;
            }
            const plain = (orders) => Object.fromEntries(totalsByCustomer(orders));
        '''),
        js_checks=[("plain([[\"ana\", 500], [\"bo\", 200], [\"ana\", 250]])", {"ana": 750, "bo": 200}),
                   ("plain([])", {}), ("plain([[\"constructor\", 1], [\"constructor\", 2]])", {"constructor": 3}),
                   ("plain([[\"Ana\", 1], [\"ana\", 2]])", {"Ana": 1, "ana": 2})],
    ),
))

# ---------------------------------------------------------------- 11
LESSONS.append(dict(
    id="node-utf16-strings-to-utf8",
    unit="node-data",
    title="UTF-16 strings vs UTF-8 String",
    concept="UTF-8 bytes, chars and lengths",
    minutes=12,
    kind="runnable",
    summary="JavaScript strings count UTF-16 code units; a Rust `String` is UTF-8, `len()` counts bytes and `chars()` yields Unicode scalar values.",
    rule="`len()` counts UTF-8 bytes and `chars().count()` counts Unicode scalar values; neither counts graphemes, and a `String` cannot be indexed by position.",
    explanation=[
        "A JavaScript string is a sequence of UTF-16 code units. `\"café\".length` is `4`, but `\"👍\".length` is `2`, because the emoji needs a surrogate pair, while `[...\"👍\"].length` is `1` because the string iterator walks code points. Indexing and `slice` work on code units, so `\"👍👍👍\".slice(0, 1)` returns half a character and the truncated output prints a replacement character.",
        "A Rust `String`, like a borrowed `&str`, is UTF-8. `len()` is the byte length: `\"café\".len()` is `5` because `é` takes two bytes, and `\"👍\".len()` is `4`. `chars()` yields `char` values, which are Unicode scalar values, so `\"👍\".chars().count()` is `1`. Neither number counts characters as a reader sees them: `\"👍🏽\"` is one grapheme but two scalar values, and grapheme segmentation needs a crate such as `unicode-segmentation`.",
        "Because a byte offset may fall inside a character, `text[0]` does not compile at all. Slicing by a byte range is allowed but panics if a bound is not on a character boundary, while `text.get(0..4)` returns `None` instead. For the first character use `text.chars().next()`, and for the first n characters `text.chars().take(n).collect::<String>()`.",
        "Case conversion works on characters too. `char::to_uppercase` returns an iterator because one character can become several: `ß` becomes `SS`, the same answer JavaScript's `toUpperCase` gives. `flat_map(char::to_uppercase)` collects them all.",
    ],
    from_lang="javascript",
    from_label="JavaScript (Node.js)",
    from_code=code(r'''
        const word = "café";
        const thumbs = "👍";

        console.log(word.length, thumbs.length, [...thumbs].length);
        console.log(Buffer.byteLength(word), Buffer.byteLength(thumbs));

        function truncate(text, max) {
          return text.length <= max ? text : text.slice(0, max - 1) + "…";
        }
        console.log(truncate("👍👍👍", 2)); // keeps half a surrogate pair
    '''),
    from_stdout="4 2 1\n5 4\n�…\n",
    from_caption="`length` and `slice` count UTF-16 code units, so truncating emoji keeps half a surrogate pair.",
    example=code(r'''
        fn truncate(text: &str, max: usize) -> String {
            if text.chars().count() <= max {
                return text.to_string();
            }
            let kept: String = text.chars().take(max.saturating_sub(1)).collect();
            kept + "…"
        }

        fn main() {
            let word = "café";
            let thumbs = "👍";
            println!("{} {} {}", word.len(), thumbs.len(), thumbs.chars().count());
            println!("{:?}", word.get(0..4));
            println!("{}", truncate("👍👍👍", 2));
        }
    '''),
    example_stdout="5 4 1\nNone\n👍…\n",
    example_caption="Byte length, scalar count and a checked slice: `get(0..4)` is `None` because byte 4 falls inside `é`.",
    contrasts=[
        ("`\"café\".length` is `4` UTF-16 code units.",
         "`\"café\".len()` is `5` UTF-8 bytes, and `chars().count()` is `4`."),
        ("`\"👍\".length` is `2`: a surrogate pair.",
         "`\"👍\".len()` is `4` and `\"👍\".chars().count()` is `1`."),
        ("`text[0]` returns the first code unit, possibly half a character.",
         "`text[0]` does not compile; use `text.chars().next()`."),
        ("`slice(0, n)` can cut a surrogate pair in half.",
         "`&text[..n]` panics off a character boundary, and `text.get(..n)` returns `None`."),
    ],
    credits=["basics/strings", "basics/chars-and-text"],
    practice=code(r'''
        fn main() {
            let word = String::from("café");
            let first = word[0];
            println!("{first}");
        }
    '''),
    practice_expect={"errors": ["E0277"], "messages": ["cannot be indexed by `{integer}`"]},
    question="What does `\"café\".len()` return in Rust, where JavaScript's `\"café\".length` is `4`?",
    answers=[
        "`4`, the number of characters",
        "`5`, the number of UTF-8 bytes",
        "`8`, the number of UTF-16 bytes",
    ],
    correct=1,
    feedback="`len()` is the byte length of the UTF-8 encoding. `é` (U+00E9) takes two bytes, so the total is 5.",
    task="Port the JavaScript `initials` shown at the top of solution.rs. Take the first character of each whitespace-separated word and uppercase it, without byte indexing, so names such as `élodie durand` and `𝒜da lovelace` work. In the Crabrix app, open the compiler lab and complete the supplied function in solution.rs. The reading question is a separate exercise.",
    success="The local compiler accepts the changed solution and the separate verification harness passes every case, including accented and non-BMP initials, `ß` and extra spaces. Printing a success message alone does not complete this lab.",
    misconception="“`len()` is the number of characters, like `.length`.”",
    correction="`len()` counts UTF-8 bytes. Count Unicode scalar values with `chars().count()`, and remember that even that is not a count of user-perceived characters.",
    trace=[
        ("Measure three ways", "`\"café\"` has 4 scalar values and 5 UTF-8 bytes; JavaScript reports 4 UTF-16 code units. `\"👍\"` has 1 scalar value, 4 bytes and 2 code units."),
        ("Check the slice", "`word.get(0..4)` asks for bytes 0 to 3. Byte 3 is the first of the two bytes of `é`, so the range would split a character and `get` returns `None`."),
        ("Compare with evidence", "Run it: `5 4 1`, `None`, then `👍…`. JavaScript's `truncate` printed a replacement character because it kept half a surrogate pair."),
    ],
    transfer="Print `\"👍🏽\".len()`, `\"👍🏽\".chars().count()` and the `char`s themselves with `{:?}`. Then predict JavaScript's `\"👍🏽\".length` and `[...\"👍🏽\"].length` before you check them in Node.",
    connections=[("previous", "Objects and Map vs HashMap", "Keyed data with HashMap and entry"),
                 ("next", "Shared references vs ownership", "Moves instead of shared references")],
    recall=[
        dict(question="Why does this panic, and what is a safe replacement?",
             code=code(r'''
                 let name = "élodie";
                 let first = &name[..1];
                 println!("{first}");
             '''),
             answer="Byte 1 is inside `é`, which takes two bytes, so the slice would split a character and panics at runtime. Use `name.chars().next()` for the first `char`, or `name.get(..1)`, which returns `None` instead of panicking.",
             expect={"panic": "is not a char boundary"}),
        dict(question="For `s = \"👍\"`, what are `s.len()`, `s.chars().count()` and JavaScript's `s.length`?",
             answer="`4` UTF-8 bytes, `1` Unicode scalar value and `2` UTF-16 code units. None of them counts graphemes: a skin-tone emoji such as `👍🏽` is one grapheme but two scalar values."),
    ],
    challenge=dict(
        function="initials",
        starter=code(r'''
            // JavaScript original:
            // function initials(name) {
            //   return name.split(" ").filter(Boolean)
            //     .map((part) => part[0].toUpperCase()).join("");
            // }
            // part[0] is one UTF-16 code unit, so it breaks on characters outside the BMP.
            pub fn initials(name: &str) -> String {
                todo!("implement the contract")
            }
        '''),
        cases=[
            ("visible", "solution::initials(\"ada lovelace\")", "\"AL\""),
            ("boundary", "solution::initials(\"  grace   hopper \")", "\"GH\""),
            ("semantic", "solution::initials(\"élodie durand\")", "\"ÉD\""),
            ("semantic", "solution::initials(\"𝒜da lovelace\")", "\"𝒜L\""),
            ("semantic", "solution::initials(\"ßen x\")", "\"SSX\""),
            ("boundary", "solution::initials(\"\")", "\"\""),
        ],
        solution=code(r'''
            pub fn initials(name: &str) -> String {
                name.split_whitespace()
                    .filter_map(|part| part.chars().next())
                    .flat_map(char::to_uppercase)
                    .collect()
            }
        '''),
        wrong=[
            ("byte slice of the first letter", code(r'''
                pub fn initials(name: &str) -> String {
                    name.split_whitespace().map(|part| part[..1].to_uppercase()).collect()
                }
            ''')),
            ("first byte read as a char", code(r'''
                pub fn initials(name: &str) -> String {
                    name.split_whitespace()
                        .map(|part| (part.as_bytes()[0] as char).to_ascii_uppercase())
                        .collect()
                }
            ''')),
            ("ASCII-only uppercase", code(r'''
                pub fn initials(name: &str) -> String {
                    name.split_whitespace()
                        .filter_map(|part| part.chars().next())
                        .map(|c| c.to_ascii_uppercase())
                        .collect()
                }
            ''')),
        ],
        js_lang="javascript",
        js_original=code(r'''
            function initials(name) {
              return name.split(" ").filter(Boolean)
                .map((part) => part[0].toUpperCase()).join("");
            }
        '''),
        js_checks=[("initials(\"ada lovelace\")", "AL"), ("initials(\"  grace   hopper \")", "GH"),
                   ("initials(\"élodie durand\")", "ÉD"), ("initials(\"𝒜da lovelace\")", "\ud835L"),
                   ("initials(\"ßen x\")", "SSX"), ("initials(\"\")", "")],
    ),
))
