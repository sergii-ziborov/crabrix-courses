#!/usr/bin/env python3
"""Build academy/learning-paths.json: alternative navigation over existing lessons.

A learning path never copies a lesson. Each step names an existing course and lesson ID,
so progress made anywhere in the Academy counts on every path that contains the lesson.
Bridge paths skip the Academy lessons their bridge course already credits.
Run from the repository root; tests/test_academy_metadata.py checks the result.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COURSES = ROOT / "courses"


def course(course_id: str) -> dict:
    return json.loads((COURSES / course_id / "course.json").read_text())


def unit_lessons(course_id: str, *unit_ids: str) -> list[tuple[str, str]]:
    ids = unit_ids or tuple(course(course_id)["unitIDs"])
    steps = []
    for unit_id in ids:
        unit = json.loads((COURSES / course_id / "units" / f"{unit_id}.json").read_text())
        steps += [(course_id, lesson_id) for lesson_id in unit["lessonIDs"]]
    return steps


def picks(course_id: str, *lesson_ids: str) -> list[tuple[str, str]]:
    return [(course_id, lesson_id) for lesson_id in lesson_ids]


def credited(course_id: str) -> set[tuple[str, str]]:
    result = set()
    for _, lesson_id in unit_lessons(course_id):
        lesson = json.loads((COURSES / course_id / "lessons" / f"{lesson_id}.json").read_text())
        result |= {tuple(target.split("/")) for target in lesson.get("bridge", {}).get("credits", [])}
    return result


def unique(steps: list[tuple[str, str]], skip: set[tuple[str, str]] = frozenset()) -> list[tuple[str, str]]:
    seen, result = set(), []
    for step in steps:
        if step not in seen and step not in skip:
            seen.add(step)
            result.append(step)
    return result


node_skip = credited("rust-for-nodejs-developers")
c_skip = credited("rust-for-c-developers")
async_interview = picks("interview", "q-async-vs-threads", "q-blocking-async", "q-cancellation",
                        "q-pin-future", "q-future-send", "q-async-locks", "q-async-traits")

PATHS = [
    ("rust-from-zero", "Rust from Zero", "People who are new to Rust, or new to programming in a compiled language",
     "Start with what Rust is, then values, functions, control flow and data modelling, then ownership, "
     "abstractions, a first Cargo project and threads.",
     unique(unit_lessons("basics") + unit_lessons("ownership", "ownership", "abstraction")
            + unit_lessons("projects", "projects") + unit_lessons("concurrency", "threads"))),
    ("rust-for-nodejs", "Rust for Node.js Developers", "JavaScript, TypeScript and Node.js developers",
     "The Node.js bridge course first: it puts your habits next to Rust and covers 30+ Academy lessons. "
     "Then ownership in depth, traits, error design, a CLI and an HTTP API, and async Rust with backpressure "
     "and shutdown, the parts a backend developer needs next.",
     unique(unit_lessons("rust-for-nodejs-developers")
            + picks("ownership", "slices", "copy-clone", "lifetimes-intro", "closures", "generics", "lifetimes",
                    "closure-capture-modes", "trait-objects", "owned-or-borrowed", "fromstr-domain-values")
            + picks("projects", "modules", "testing", "error-context", "serde-roundtrip-validation",
                    "route-cli-arguments", "route-cli-exit", "route-http-routing", "route-http-json",
                    "route-http-idempotency", "route-sql-query")
            + picks("concurrency", "async-runtime", "async-patterns", "async-cancellation", "blocking-async",
                    "joinset-task-ownership", "semaphore-backpressure", "graceful-shutdown-protocol"),
            node_skip)),
    ("rust-for-c", "Rust for C Developers", "Programmers who know C: pointers, malloc and free, make",
     "The C bridge course first: it maps malloc/free, pointers, errno and tagged unions onto Rust and covers "
     "30+ Academy lessons. Then borrowing rules in depth, smart pointers, FFI and layout, unsafe contracts, "
     "and threads with atomics.",
     unique(unit_lessons("rust-for-c-developers")
            + picks("ownership", "mutable-borrows", "reborrowing", "lifetimes", "interior-mutability-intro",
                    "generics", "traits", "trait-objects", "iterators")
            + picks("projects", "box", "rc-refcell", "deref-drop", "cycles", "errors", "testing")
            + picks("systems", "ffi", "repr-layout", "unsafe-traits", "performance", "benchmarking-profiling",
                    "wasm-linear-memory")
            + picks("concurrency", "channels", "send-sync", "scoped-threads", "atomics-basics", "deadlock-avoidance"),
            c_skip)),
    ("rust-for-experienced", "Rust for Experienced Programmers", "Developers fluent in another language",
     "Skip the syntax tour: what Rust is, reading rustc, then ownership, borrowing, traits and generics, "
     "errors as values, modules and tests, and the concurrency model.",
     unique(picks("basics", "what-is-rust", "compiler-feedback", "enums", "pattern-matching", "option-result",
                  "recoverable-errors")
            + picks("ownership", "ownership", "borrowing", "slices", "copy-clone", "lifetimes-intro",
                    "mutable-borrows", "owned-or-borrowed", "generics", "traits", "closures", "iterators",
                    "trait-objects", "lifetimes")
            + picks("projects", "modules", "errors", "testing", "dependencies")
            + picks("concurrency", "concurrency", "shared-state", "send-sync", "futures", "async-runtime"))),
    ("rust-backend", "Rust Backend Development", "Developers building CLIs, HTTP services and data pipelines",
     "Errors with context, validated data, a CLI contract, HTTP routing and JSON, SQL with transactions, "
     "diagnostics and a repeatable release, then async task ownership and backpressure.",
     unique(picks("projects", "errors", "error-context", "validated-records", "serde-roundtrip-validation")
            + unit_lessons("projects", "route-cli", "route-http", "route-sql", "route-diagnostics", "route-delivery")
            + unit_lessons("concurrency", "async-operations"))),
    ("async-rust", "Async Rust", "Developers who need futures, runtimes and cancellation",
     "Futures and runtimes, join and select, pinning, cancellation safety, blocking, task ownership, "
     "backpressure and graceful shutdown, with interview questions to check understanding.",
     unique(unit_lessons("concurrency", "async", "async-reliability", "async-operations") + async_interview)),
    ("systems-programming", "Systems Programming", "Developers working close to memory, FFI and WebAssembly",
     "Macros, unsafe Rust and its invariants, FFI, layout, performance measurement and WebAssembly, "
     "with interior mutability and atomics.",
     unique(unit_lessons("systems") + picks("ownership", "interior-mutability-intro")
            + unit_lessons("concurrency", "concurrency-safety"))),
    ("rust-interview", "Rust Interview Preparation", "Candidates preparing for Rust interviews",
     "All interview topics: language, async, systems, APIs and live coding.",
     unique(unit_lessons("interview"))),
]

payload = {
    "schemaVersion": 1,
    "description": "Learning paths are navigation over existing Academy lessons; they never copy a lesson.",
    "paths": [
        {"id": path_id, "title": title, "audience": audience, "description": description,
         "steps": [{"courseId": course_id, "lessonId": lesson_id} for course_id, lesson_id in steps]}
        for path_id, title, audience, description, steps in PATHS
    ],
}
(ROOT / "academy" / "learning-paths.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
print({path["id"]: len(path["steps"]) for path in payload["paths"]})
