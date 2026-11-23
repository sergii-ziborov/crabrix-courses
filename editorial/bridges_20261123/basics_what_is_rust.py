#!/usr/bin/env python3
"""Add "What Rust Is" as the first Rust Basics lesson (Basics 1.0.10).

Existing lesson IDs, answers and checks are unchanged; only the Foundations
lesson order shifts by one. Code claims (output `area = 12`, E0308, E0600) were
checked with rustc 1.89.0 and 1.100.0 — see verify_what_is_rust.py.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "courses" / "basics"
EXAMPLE = 'fn area(width: u32, height: u32) -> u32 {\n    width * height\n}\n\nfn main() {\n    let room = area(4, 3);\n    println!("area = {room}");\n}'
PRACTICE = EXAMPLE.replace("area(4, 3)", 'area(4, "3")')

lesson = {
    "id": "what-is-rust",
    "parentID": "foundations",
    "order": 0,
    "title": "What Rust Is",
    "concept": "A compiled language without a garbage collector",
    "minutes": 7,
    "exerciseKind": "planned",
    "writing": {
        "summary": "Rust is a compiled, statically typed language without a garbage collector. The compiler checks types, ownership and borrowing before your program runs, then produces a native program.",
        "rule": "Rust is a compiled, statically typed language without a garbage collector: rustc checks types, ownership and borrowing before the program runs, then produces a native executable.",
        "explanation": "\n\n".join([
            "Rust is a general-purpose programming language for software where speed, predictable memory use and correctness all matter: command-line tools, web servers, embedded devices, WebAssembly modules, and parts of operating systems and browsers. Its first stable version, Rust 1.0, was released in May 2015. A new stable compiler is published every six weeks, and editions such as Rust 2024 let the language evolve without breaking code written for an earlier edition.",
            "Rust is compiled ahead of time. The compiler, `rustc`, reads your source, checks it, and translates it through LLVM into machine code for a target: an iPhone, a Linux server, or `wasm32-wasip1`, the WebAssembly target Crabrix uses to run your programs on the device. The result runs on its own; no interpreter or virtual machine has to be installed. Languages that run source directly, such as Python, or compile it while running, such as JavaScript in V8, discover many mistakes, like calling a method that does not exist, only when the faulty line executes.",
            "Rust is statically typed. Every value has a type the compiler knows, such as `u32`, `String` or `bool`. The compiler often infers types, so you do not write them everywhere, but it never guesses them while the program runs. In the example, `area` promises to take two `u32` values and return one. Passing the text `\"3\"` instead is error `E0308`, mismatched types, and no program is built, so a program with that mistake never exists.",
            "Rust has no garbage collector, and you do not call `free` either. Each value has one owner, and the value is dropped, its memory released, exactly when that owner goes out of scope. The compiler enforces these ownership and borrowing rules, which is how safe Rust rules out use after free, double frees and data races without a collector running in the background. The rules are introduced gradually in this course and explained in depth in Ownership Mastery.",
            "Two tools do the work. `rustc` compiles a crate; Cargo builds whole projects, runs tests and downloads libraries, called crates, from crates.io. In Crabrix the compiler is part of the app, so Run performs both steps on your device: compile, and only if that succeeds, execute.",
        ]),
        "exampleCaption": "Before anything runs, `rustc` checks that `area` gets two `u32` values and returns one; the built program then prints `area = 12`.",
        "exampleCode": EXAMPLE,
        "task": "Change the call to `area(4, \"3\")` and build. Note the error code and the line rustc points to, then restore the number and run it again.",
        "success": "You can explain what happens before a Rust program runs: rustc checks types and ownership, and only a program that passes those checks is built and executed.",
        "practiceCode": PRACTICE,
        "question": "`area` takes two `u32` values. What happens when you build `area(4, \"3\")`?",
        "answers": [
            "It builds, then crashes at run time when `area` multiplies a number by text",
            "rustc reports `E0308` mismatched types, and no new program is built",
            "Rust converts `\"3\"` to the number 3 automatically",
            "It builds with a warning and passes 0 for the text",
        ],
        "correctAnswer": 1,
        "feedback": "Rust is statically typed and compiled ahead of time: the mismatch is found while building, so no program containing the mistake is produced.",
        "recall": [
            {"question": "Rust has no garbage collector. What frees a `String` once your program no longer needs it?",
             "answer": "Its owner going out of scope. When the variable that owns the `String` leaves its scope, Rust drops the value and frees its memory exactly once. You never call `free`, and no collector runs in the background."},
            {"question": "Why can a Rust program with a type error never run, not even once?",
             "answer": "Rust is compiled ahead of time. `rustc` checks types before it produces an executable; when a check fails it reports an error such as `E0308` and builds nothing, so there is no program to run."},
        ],
    },
    "depth": {
        "traceSteps": [
            {"title": "Write", "detail": "You write `area(4, 3)` in `main.rs`. Nothing runs yet; it is only source text."},
            {"title": "Compile", "detail": "`rustc` checks types, ownership and borrowing, then translates the program into machine code, or a WebAssembly module in Crabrix."},
            {"title": "Run", "detail": "Only the built program runs. It prints `area = 12`; the compiler is no longer involved."},
        ],
        "misconception": "“No garbage collector means I have to free memory myself, like in C”",
        "correction": "Memory is released automatically, at a point the compiler can see: when the owner goes out of scope. There is no `free` call to forget and no collector pausing the program.",
        "transferChallenge": "Call `area(4, -3)` and predict the diagnostic before you build. Then explain why it appears before anything is printed.",
        "connections": [{"direction": "next", "title": "Hello, Rust", "concept": "Functions and stdout"}],
    },
}

(ROOT / "lessons" / "what-is-rust.json").write_text(json.dumps(lesson, indent=2, ensure_ascii=False) + "\n")
(ROOT / "checks" / "what-is-rust.json").write_text(json.dumps(
    {"evidence": {"correctAnswer": 1, "kind": "reasoning"}}, indent=2) + "\n")

unit_path = ROOT / "units" / "foundations.json"
unit = json.loads(unit_path.read_text())
if unit["lessonIDs"][0] != "what-is-rust":
    unit["lessonIDs"].insert(0, "what-is-rust")
unit_path.write_text(json.dumps(unit, indent=2, ensure_ascii=False) + "\n")
for order, lesson_id in enumerate(unit["lessonIDs"]):
    path = ROOT / "lessons" / f"{lesson_id}.json"
    data = json.loads(path.read_text())
    data["order"] = order
    if lesson_id == "hello-rust" and not any(c["direction"] == "previous" for c in data["depth"]["connections"]):
        data["depth"]["connections"].insert(0, {"direction": "previous", "title": "What Rust Is",
                                                "concept": "A compiled language without a garbage collector"})
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

for name in ("course.json", "provenance.json"):
    path = ROOT / name
    data = json.loads(path.read_text())
    data["contentVersion"] = "1.0.10"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print("what-is-rust added; Basics 1.0.10")
