#!/usr/bin/env python3
"""Write the rust-for-c-developers CoursePack sources from lessons_src/*.py.

Each lesson module defines ID, UNIT, ORDER, LESSON and optionally CHALLENGE
and EXPECT (EXPECT is verification data and never enters the pack). Lessons
that do not exist yet are simply left out, so a partial course stays valid.
Run: python3 -I editorial/bridges_20261123/rust-for-c-developers/author.py
"""

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
COURSE_ID = "rust-for-c-developers"
OUT = REPO / "courses" / COURSE_ID
STUB = 'todo!("implement the contract")'

COURSE = {
    "contentVersion": "1.0.0",
    "id": COURSE_ID,
    "language": "en",
    "level": "FOR C DEVELOPERS",
    "order": 8,
    "subtitle": "Map malloc/free, pointers, errno, tagged unions and make onto ownership, "
                "borrows, Result, enums and Cargo",
    "systemImage": "c.square.fill",
    "theme": "bridges",
    "title": "Rust for C Developers",
}

UNITS = [
    ("c-syntax", "Familiar syntax, different defaults",
     "printf, const, integer rules, expressions and loops"),
    ("c-memory", "Memory without malloc and free",
     "Owners, borrows, slices and lifetimes instead of conventions"),
    ("c-data", "Data, absence and errors",
     "Methods, tagged unions, NULL, errno and text"),
    ("c-systems", "Build, unsafe, FFI and threads",
     "Cargo, the unsafe boundary and data-race-free threads"),
]

TERMS = [
    ("c-ownership", "Ownership", "Like the C rule that whoever calls malloc frees, but checked: each value has one owner, and dropping the owner frees it.", "c-malloc-free-to-ownership"),
    ("c-drop", "Drop", "The destructor that runs exactly once when the owner goes out of scope; it replaces free calls and goto cleanup chains.", "c-malloc-free-to-ownership"),
    ("c-shared-ref", "&T", "A shared reference: like a const pointer that is never null and never dangles, and nothing mutates the value while it is in use.", "c-pointers-to-references"),
    ("c-mut-ref", "&mut T", "An exclusive reference: what restrict promises, enforced by the compiler; no other access while it is in use.", "c-pointers-to-references"),
    ("c-slice", "&[T]", "A slice: a pointer and a length travelling together, with bounds-checked indexing.", "c-pointer-length-to-slices"),
    ("c-lifetime", "Lifetime", "A compile-time name for how long a pointee stays valid, the fact a C API documents in a comment.", "c-dangling-pointers-to-lifetimes"),
    ("c-copy", "Copy", "Implicit bitwise duplication, like C struct assignment, allowed only for types that own no resources.", "c-struct-copy-to-copy-clone"),
    ("c-enum", "enum", "A tagged union whose tag and payload cannot disagree; match must handle every variant.", "c-tagged-unions-to-enums"),
    ("c-option", "Option<T>", "Replaces a NULL return: None is a separate value the caller must handle before using the payload.", "c-null-and-errno-to-option-result"),
    ("c-result", "Result<T, E>", "Replaces -1 plus errno: the error travels in the return value and cannot be overwritten.", "c-null-and-errno-to-option-result"),
    ("c-string", "String", "An owned, growable UTF-8 buffer with a stored length and no NUL terminator.", "c-char-arrays-to-strings"),
    ("c-crate", "Crate", "The unit of compilation: a whole tree of modules, not a single .c file.", "c-make-and-headers-to-cargo"),
    ("c-pub", "pub", "The export marker; items are private to their module otherwise, the reverse of C's external linkage default.", "c-make-and-headers-to-cargo"),
    ("c-unsafe", "unsafe", "A block where you, not the compiler, prove the invariants C always left to you.", "c-unsafe-and-ffi"),
    ("c-repr-c", "#[repr(C)]", "Lays out a struct with C's field order and padding rules for the target.", "c-unsafe-and-ffi"),
    ("c-mutex", "Mutex<T>", "A lock that owns the data it protects; the guard unlocks when it is dropped.", "c-pthreads-to-threads"),
]


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lesson_modules():
    modules = [load_module(p) for p in sorted((HERE / "lessons_src").glob("*.py"))]
    return sorted(modules, key=lambda m: ([u[0] for u in UNITS].index(m.UNIT), m.ORDER))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def challenge_check(lid: str, challenge: dict) -> dict:
    expected = f"PASS {lid}\n"
    required = [f"pub fn {name}" for name in challenge["functions"]]
    forbidden = [STUB]
    return {
        "challenge": {
            "lessonID": lid,
            "patternID": lid,
            "projectName": f"{lid}-lab",
            "source": challenge["source"],
            "verificationSource": challenge["harness"],
            "verificationCases": [
                {"kind": kind, "input": given, "expectedAnswer": answer}
                for kind, given, answer in challenge["cases"]
            ],
            "expectedOutput": expected,
            "requiredSourceFragments": required,
            "forbiddenSourceFragments": forbidden,
        },
        "evidence": {
            "kind": "algorithmChallenge",
            "expectedOutput": {"kind": "exact", "value": expected},
            "requiredSourceFragments": required,
            "forbiddenSourceFragments": forbidden,
        },
    }


def main() -> None:
    modules = lesson_modules()
    kept_illustrations = {}
    for path in (OUT / "lessons").glob("*.json") if (OUT / "lessons").exists() else []:
        previous = json.loads(path.read_text(encoding="utf-8"))
        if "illustration" in previous:
            kept_illustrations[previous["id"]] = previous["illustration"]
    for stale in ("lessons", "checks", "projects", "units"):
        folder = OUT / stale
        if folder.exists():
            for path in sorted(folder.rglob("*"), reverse=True):
                path.unlink() if path.is_file() else path.rmdir()
    present_units = []
    for unit_order, (uid, title, subtitle) in enumerate(UNITS):
        unit_lessons = [m for m in modules if m.UNIT == uid]
        if not unit_lessons:
            continue
        lesson_ids = []
        for order, module in enumerate(unit_lessons):
            lid = module.ID
            lesson = {"concept": module.LESSON["concept"], "depth": module.LESSON["depth"],
                      "exerciseKind": module.LESSON["exerciseKind"], "id": lid,
                      "minutes": module.LESSON["minutes"], "order": order, "parentID": uid,
                      "title": module.LESSON["title"], "writing": module.LESSON["writing"],
                      "bridge": module.LESSON["bridge"]}
            if lid in kept_illustrations and (OUT / kept_illustrations[lid]["path"]).exists():
                lesson["illustration"] = kept_illustrations[lid]
            write(OUT / "lessons" / f"{lid}.json", lesson)
            challenge = getattr(module, "CHALLENGE", None)
            if lesson["exerciseKind"] == "runnable":
                write(OUT / "checks" / f"{lid}.json", challenge_check(lid, challenge))
                write(OUT / "projects" / lid / "project.json",
                      {"name": f"{lid}-lab", "entryFile": "solution.rs"})
                write(OUT / "projects" / lid / "solution.rs", challenge["source"])
            else:
                write(OUT / "checks" / f"{lid}.json",
                      {"evidence": {"correctAnswer": lesson["writing"]["correctAnswer"],
                                    "kind": "reasoning"}})
            lesson_ids.append(lid)
        write(OUT / "units" / f"{uid}.json",
              {"id": uid, "lessonIDs": lesson_ids, "level": unit_order + 1,
               "order": len(present_units), "parentID": COURSE_ID,
               "subtitle": subtitle, "title": title})
        present_units.append(uid)
    write(OUT / "course.json", {**COURSE, "unitIDs": present_units})
    present = {m.ID for m in modules}
    write(OUT / "terms.json", [
        {"description": description, "id": tid, "order": order, "term": term, "topic": topic}
        for order, (tid, term, description, topic) in enumerate(
            t for t in TERMS if t[3] in present)
    ])
    write(OUT / "provenance.json", {
        "contentVersion": COURSE["contentVersion"],
        "courseID": COURSE_ID,
        "editorialRevision": "bridges_20261123",
        "sourceURL": "https://github.com/sergii-ziborov/crabrix-courses",
    })
    print(f"Wrote {len(modules)} lessons in {len(present_units)} units to {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
