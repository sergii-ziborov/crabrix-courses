ID = "c-make-and-headers-to-cargo"
UNIT = "c-systems"
ORDER = 0

FROM_CODE = r'''#include <stdio.h>

/* geometry.h would declare:  int area(int w, int h);
   Every function below that is not `static` is visible at link time. */

static int clamp_positive(int v) {      /* internal linkage: this file only */
    return v < 0 ? 0 : v;
}

int area(int w, int h) {                /* external linkage: exported by default */
    return clamp_positive(w) * clamp_positive(h);
}

int main(void) {
    printf("%d %d\n", area(3, 4), area(-2, 5));
    return 0;
}

/* Makefile:
   app: main.o geometry.o
       cc -o app main.o geometry.o
   geometry.o: geometry.c geometry.h    # forget the header here: a stale build */
'''

EXAMPLE = r'''// In a Cargo package this module body lives in src/geometry.rs,
// and `mod geometry;` in src/main.rs or src/lib.rs loads it.
mod geometry {
    fn clamp_positive(v: i32) -> i32 { // private by default: this module only
        v.max(0)
    }

    pub fn area(w: i32, h: i32) -> i32 { // `pub` is the export
        clamp_positive(w) * clamp_positive(h)
    }
}

fn main() {
    println!("{} {}", geometry::area(3, 4), geometry::area(-2, 5));
}
'''

PRACTICE = r'''mod geometry {
    fn clamp_positive(v: i32) -> i32 {
        v.max(0)
    }

    pub fn area(w: i32, h: i32) -> i32 {
        clamp_positive(w) * clamp_positive(h)
    }
}

fn main() {
    println!("{}", geometry::area(3, 4));
    println!("{}", geometry::clamp_positive(-1));
}
'''

LESSON = {
    "title": "Headers and make to Cargo",
    "concept": "Modules, pub and the crate as the build unit",
    "minutes": 11,
    "exerciseKind": "planned",
    "writing": {
        "summary": "Cargo replaces headers and Makefiles: the crate is the unit of compilation, modules are found from `mod` declarations, and items are private until marked `pub`.",
        "rule": "Items are private to their module unless marked `pub`; `src/main.rs` is the default binary target and `src/lib.rs` the library target.",
        "explanation": (
            "A C project splits declarations into headers, definitions into `.c` files, and the build graph into a Makefile that must list which object depends on which header. Every function that is not `static` has external linkage and is visible to any translation unit that declares it, and a missing header dependency in the Makefile gives you a stale build that links old code.\n\n"
            "In Rust the unit of compilation is the crate, a tree of modules compiled together, not a single file. There are no headers: `mod geometry;` in `src/main.rs` or `src/lib.rs` tells the compiler to load `src/geometry.rs` (or `src/geometry/mod.rs`), and the compiler reads the definitions directly. Because rustc sees the whole crate and Cargo records which files each build read, there is no dependency list to keep in sync.\n\n"
            "Visibility is the reverse of C. Everything is private to its module by default, like `static` at file scope, and `pub` is the export. Calling a private function from another module is error `E0603`. `pub(crate)` exports an item to the whole crate but not to its users, which is what most internal C helpers wanted to be.\n\n"
            "Cargo's conventions replace the Makefile. `Cargo.toml` names the package and its dependencies, `src/main.rs` is the default binary and `src/lib.rs` the library. A package may have both, in which case `main.rs` uses the library through the package name, like any outside user would. `cargo build` compiles, `cargo run` builds and runs, `cargo check` type-checks without generating code, and `cargo test` runs the tests."
        ),
        "exampleCode": EXAMPLE,
        "exampleCaption": "One file stands in for `src/geometry.rs`: `clamp_positive` is private to the module, and only `pub fn area` is visible to `main`.",
        "practiceCode": PRACTICE,
        "task": "Work out how `main.rs` reaches a function in `src/geometry.rs` when a package has both `src/lib.rs` and `src/main.rs`, then fix the practice program's call to a private function.",
        "success": "You can name the two declarations that make `geometry::area` callable from `main.rs`, `pub mod geometry;` in `lib.rs` and `pub fn area`, and the path `main.rs` uses.",
        "question": "A package named `shapes` has `src/lib.rs`, `src/main.rs` and `src/geometry.rs`. How does `main.rs` call `area` from `geometry.rs`?",
        "answers": [
            "`#include \"geometry.rs\"` at the top of `main.rs`",
            "Mark `area` as `extern` so that the linker finds it",
            "`lib.rs` declares `pub mod geometry;`, `area` is `pub`, and `main.rs` calls `shapes::geometry::area`",
            "`main.rs` calls `geometry::area` directly, because both files are in `src/`",
        ],
        "correctAnswer": 2,
        "feedback": "Files are not compilation units: `mod` puts `geometry.rs` into the library crate, `pub` exports it, and the binary crate uses the library through the package name.",
        "recall": [
            {
                "question": "What does `pub(crate)` give you that C's `static` and default external linkage do not?",
                "answer": "A middle level of visibility: the item is usable from every module in the crate but not by users of the crate. C has file-private (`static`) and global (everything else), with no boundary at the library.",
            },
            {
                "question": "Which Cargo command replaces running `make` just to see whether the code compiles, and why is it faster?",
                "answer": "`cargo check`. It runs the compiler's analysis, including type and borrow checking, without generating machine code, so it is the quickest way to see every compiler error.",
            },
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Turn headers into modules", "detail": "For each `.c` and `.h` pair, create one `name.rs` and a `mod name;` line in its parent module."},
            {"title": "Choose the exports", "detail": "Mark `pub` only what other modules call; leave the rest private, as `static` would have."},
            {"title": "Pick the targets", "detail": "Put reusable code in `src/lib.rs`, the entry point in `src/main.rs`, and call the library through the package name."},
        ],
        "misconception": "“`mod geometry;` is Rust's `#include`.”",
        "correction": "`#include` pastes text into the translation unit. `mod geometry;` declares a module and tells the compiler where its source is; the module has its own namespace and privacy, and it is compiled once as part of the crate.",
        "transferChallenge": "Run `cargo new shapes`, add `src/lib.rs` with `pub mod geometry;` and `src/geometry.rs`, and call `shapes::geometry::area` from `src/main.rs`; then make `area` private and read the error.",
        "connections": [
            {"direction": "previous", "title": "char Arrays to Strings", "concept": "Owned UTF-8 with a length, not a NUL"},
            {"direction": "next", "title": "unsafe, Raw Pointers and FFI", "concept": "Where Rust hands the proof back to you"},
        ],
    },
    "bridge": {
        "from": "c",
        "fromLabel": "C",
        "fromCode": FROM_CODE,
        "fromCaption": "Only `static` keeps a C function file-private, and the header and Makefile dependency lists are maintained by hand.",
        "contrasts": [
            {"from": "Functions are exported unless declared `static`.",
             "rust": "Items are private unless marked `pub`; a call to a private item is `E0603`."},
            {"from": "Headers repeat declarations; the Makefile lists dependencies.",
             "rust": "`mod name;` loads `name.rs`, and Cargo tracks what each build read."},
            {"from": "The translation unit is one `.c` file.",
             "rust": "The crate is the unit: `src/main.rs` for a binary, `src/lib.rs` for a library."},
        ],
        "credits": ["projects/modules", "projects/package-layout"],
    },
}

CARGO_TOML = '[package]\nname = "shapes"\nversion = "0.1.0"\nedition = "2024"\n'
GEOMETRY = ("fn clamp_positive(v: i32) -> i32 {\n    v.max(0)\n}\n\n"
            "pub fn area(w: i32, h: i32) -> i32 {\n    clamp_positive(w) * clamp_positive(h)\n}\n")

EXPECT = {
    "example": "12 0\n",
    "practice": {"errors": ["E0603"]},
    "recall": [None, None],
    "cargo": {
        "package": "shapes",
        "files": {
            "Cargo.toml": CARGO_TOML,
            "src/lib.rs": "pub mod geometry;\n",
            "src/geometry.rs": GEOMETRY,
            "src/main.rs": "fn main() {\n    println!(\"{}\", shapes::geometry::area(3, 4));\n}\n",
        },
        "stdout": "12\n",
    },
    "c": {"warnings": [], "stdout": "12 0\n", "exit": 0},
}
