#!/usr/bin/env python3
"""Write the rust-for-nodejs-developers CoursePack sources from the lesson modules.

Run from anywhere: python3 -I editorial/bridges_20261123/rust-for-nodejs-developers/author.py
Lesson modules that do not exist yet are skipped, so the course can be written
unit by unit. Tooling adds contentDigest and illustration later; this script
keeps both if they are already present in a lesson file.
"""

import importlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[2]
COURSE_ID = "rust-for-nodejs-developers"
ROOT = REPO / "courses" / COURSE_ID
SOURCE_SHA = "31a1969499c4811f9918e72fa8e6e53416d8fcab"

UNITS = [
    ("node-values", "Values and types",
     "Bindings, numbers, functions and conditions without coercion",
     ["node-console-log-to-println", "node-let-const-to-let-mut", "node-number-to-integer-types",
      "node-functions-to-fn", "node-truthiness-to-bool-and-match"]),
    ("node-data", "Data shapes",
     "Objects, unions, null, arrays, maps and strings in Rust types",
     ["node-objects-to-structs", "node-ts-unions-to-enums", "node-null-undefined-to-option",
      "node-array-methods-to-iterators", "node-map-and-objects-to-hashmap", "node-utf16-strings-to-utf8"]),
    ("node-ownership", "What the garbage collector hid",
     "Moves, borrows and nominal traits instead of shared references",
     ["node-shared-references-to-ownership", "node-mutation-to-borrowing", "node-interfaces-to-traits"]),
    ("node-runtime", "Errors, packages and async",
     "try/catch, npm and Promises mapped to Result, Cargo and futures",
     ["node-try-catch-to-result", "node-npm-to-cargo", "node-promises-to-futures"]),
]

MODULES = ["lessons_values", "lessons_data", "lessons_ownership", "lessons_runtime"]

TERMS = [
    ("node-let-mut", "let mut", "Like a JavaScript let: the binding may change. Plain let acts like const and also freezes the value.", "node-let-const-to-let-mut"),
    ("node-checked-sub", "checked_sub", "Subtraction that returns None on overflow, where JavaScript would return a negative Number.", "node-number-to-integer-types"),
    ("node-tail-expression", "Tail expression", "A final expression without a semicolon is returned, like an arrow function's expression body.", "node-functions-to-fn"),
    ("node-match", "match", "An exhaustive switch: no fall-through, and every possible value must be covered.", "node-truthiness-to-bool-and-match"),
    ("node-mut-self", "&mut self", "A method receiver that may change fields; in a JavaScript class every method can change this.", "node-objects-to-structs"),
    ("node-enum", "enum", "A discriminated union whose variant is the tag, checked by the compiler.", "node-ts-unions-to-enums"),
    ("node-option", "Option<T>", "Replaces null and undefined: Some(value) or None, handled before the value is used.", "node-null-undefined-to-option"),
    ("node-iterator-adapter", "Iterator adapter", "A lazy map or filter that runs only when a consumer such as sum pulls items.", "node-array-methods-to-iterators"),
    ("node-entry", "HashMap::entry", "Update-or-insert with one lookup, replacing map.set(k, (map.get(k) ?? 0) + 1).", "node-map-and-objects-to-hashmap"),
    ("node-chars", "chars()", "Iterates Unicode scalar values, while JavaScript's length counts UTF-16 code units.", "node-utf16-strings-to-utf8"),
    ("node-move", "Move", "Assigning a String hands it to a new owner, where JavaScript would share one reference.", "node-shared-references-to-ownership"),
    ("node-mut-ref", "&mut T", "Exclusive borrowed access, the only way a function may change its argument.", "node-mutation-to-borrowing"),
    ("node-trait", "trait", "A nominal interface: a type satisfies it only through an explicit impl block.", "node-interfaces-to-traits"),
    ("node-result", "Result<T, E>", "Replaces throw: failure is a return value that the caller must handle.", "node-try-catch-to-result"),
    ("node-cargo-lock", "Cargo.lock", "Records the exact resolved dependency versions, like package-lock.json.", "node-npm-to-cargo"),
    ("node-future", "Future", "A lazy Promise: nothing runs until an executor polls it.", "node-promises-to-futures"),
]

TODO = 'todo!("implement the contract")'


def save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def harness(lesson: dict) -> str:
    challenge = lesson["challenge"]
    if "harness" in challenge:
        return challenge["harness"].rstrip("\n") + "\n"
    lines = ["mod solution;", "", "fn main() {"]
    for index, (_, expression, expected) in enumerate(challenge["cases"], start=1):
        lines.append(f'    assert_eq!({expression}, {expected}, "case {index}");')
    lines += ["", f'    println!("PASS {lesson["id"]}");', "}"]
    return "\n".join(lines) + "\n"


def lesson_json(lesson: dict, unit_id: str, order: int, existing: dict) -> dict:
    writing = {
        "summary": lesson["summary"], "rule": lesson["rule"],
        "explanation": "\n\n".join(lesson["explanation"]),
        "exampleCode": lesson["example"], "exampleCaption": lesson["example_caption"],
        "task": lesson["task"], "success": lesson["success"],
        "practiceCode": lesson["practice"], "question": lesson["question"],
        "answers": lesson["answers"], "correctAnswer": lesson["correct"],
        "feedback": lesson["feedback"],
        "recall": [{key: card[key] for key in ("question", "answer", "code") if key in card}
                   for card in lesson["recall"]],
    }
    depth = {
        "misconception": lesson["misconception"], "correction": lesson["correction"],
        "traceSteps": [{"title": t, "detail": d} for t, d in lesson["trace"]],
        "transferChallenge": lesson["transfer"],
        "connections": [{"direction": d, "title": t, "concept": c} for d, t, c in lesson["connections"]],
    }
    result = {
        "id": lesson["id"], "parentID": unit_id, "order": order, "title": lesson["title"],
        "concept": lesson["concept"], "minutes": lesson["minutes"], "exerciseKind": lesson["kind"],
        "writing": writing, "depth": depth,
        "bridge": {
            "from": lesson["from_lang"], "fromLabel": lesson["from_label"],
            "fromCode": lesson["from_code"], "fromCaption": lesson["from_caption"],
            "contrasts": [{"from": f, "rust": r} for f, r in lesson["contrasts"]],
            "credits": lesson["credits"],
        },
    }
    for key in ("contentDigest", "illustration"):
        if key in existing:
            result[key] = existing[key]
    return result


def check_json(lesson: dict) -> dict:
    if lesson["kind"] == "planned":
        return {"evidence": {"kind": "reasoning", "correctAnswer": lesson["correct"]}}
    challenge = lesson["challenge"]
    required = [f"pub fn {challenge['function']}"] + challenge.get("required", [])
    forbidden = [TODO] + challenge.get("forbidden", [])
    expected = f"PASS {lesson['id']}\n"
    return {
        "challenge": {
            "lessonID": lesson["id"], "patternID": lesson["id"], "projectName": f"{lesson['id']}-lab",
            "source": challenge["starter"] + "\n", "verificationSource": harness(lesson),
            "verificationCases": [{"kind": k, "input": i, "expectedAnswer": e}
                                  for k, i, e in challenge["cases"]],
            "expectedOutput": expected,
            "requiredSourceFragments": required, "forbiddenSourceFragments": forbidden,
        },
        "evidence": {
            "kind": "algorithmChallenge", "expectedOutput": {"kind": "exact", "value": expected},
            "requiredSourceFragments": required, "forbiddenSourceFragments": forbidden,
        },
    }


def main() -> None:
    lessons = {}
    for name in MODULES:
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError as error:
            if error.name != name:
                raise
            continue
        for lesson in module.LESSONS:
            lessons[lesson["id"]] = lesson
    save(ROOT / "course.json", {
        "id": COURSE_ID, "language": "en", "contentVersion": "1.0.0", "order": 9,
        "level": "FOR NODE.JS DEVELOPERS", "title": "Rust for Node.js Developers",
        "subtitle": "Map JavaScript and TypeScript habits to Rust: objects, null and undefined, array methods, try/catch, npm and Promises",
        "systemImage": "curlybraces.square.fill", "theme": "bridges",
        "unitIDs": [unit for unit, *_ in UNITS],
        **({"contentDigest": json.loads((ROOT / "course.json").read_text())["contentDigest"]}
           if (ROOT / "course.json").exists() and "contentDigest" in json.loads((ROOT / "course.json").read_text()) else {}),
    })
    save(ROOT / "provenance.json", {
        "sourceURL": "https://github.com/sergii-ziborov/crabrix-courses", "sourceSHA": SOURCE_SHA,
        "courseID": COURSE_ID, "contentVersion": "1.0.0", "editorialRevision": "bridges_20261123",
    })
    save(ROOT / "terms.json", [
        {"id": tid, "order": 2000 + index, "term": term, "description": description, "topic": topic}
        for index, (tid, term, description, topic) in enumerate(TERMS)
    ])
    expectations = {}
    for unit_order, (unit_id, title, subtitle, lesson_ids) in enumerate(UNITS):
        unit_path = ROOT / "units" / f"{unit_id}.json"
        unit = {"id": unit_id, "parentID": COURSE_ID, "order": unit_order, "level": unit_order + 1,
                "title": title, "subtitle": subtitle, "lessonIDs": lesson_ids}
        if unit_path.exists() and "contentDigest" in json.loads(unit_path.read_text()):
            unit["contentDigest"] = json.loads(unit_path.read_text())["contentDigest"]
        save(unit_path, unit)
        for order, lid in enumerate(lesson_ids):
            if lid not in lessons:
                continue
            lesson = lessons[lid]
            assert lesson["unit"] == unit_id, lid
            path = ROOT / "lessons" / f"{lid}.json"
            existing = json.loads(path.read_text()) if path.exists() else {}
            save(path, lesson_json(lesson, unit_id, order, existing))
            save(ROOT / "checks" / f"{lid}.json", check_json(lesson))
            project = ROOT / "projects" / lid
            solutions = HERE / "solutions"
            wrong_root = HERE / "wrong" / lid
            if lesson["kind"] == "runnable":
                challenge = lesson["challenge"]
                project.mkdir(parents=True, exist_ok=True)
                (project / "project.json").write_text(json.dumps(
                    {"name": f"{lid}-lab", "entryFile": "solution.rs"}, indent=2) + "\n", encoding="utf-8")
                (project / "solution.rs").write_text(challenge["starter"] + "\n", encoding="utf-8")
                solutions.mkdir(parents=True, exist_ok=True)
                (solutions / f"{lid}.rs").write_text(challenge["solution"] + "\n", encoding="utf-8")
                if wrong_root.exists():
                    shutil.rmtree(wrong_root)
                wrong_root.mkdir(parents=True)
                for index, (_, source) in enumerate(challenge["wrong"], start=1):
                    (wrong_root / f"{index}.rs").write_text(source + "\n", encoding="utf-8")
            else:
                if project.exists():
                    shutil.rmtree(project)
            expectations[lid] = {
                "kind": lesson["kind"],
                "exampleStdout": lesson["example_stdout"],
                "from": {"lang": lesson["from_lang"], "stdout": lesson["from_stdout"],
                         **({"runner": lesson["from_runner"]} if "from_runner" in lesson else {})},
                "practice": lesson["practice_expect"],
                "recall": [card.get("expect") for card in lesson["recall"]],
                **({"challenge": {
                    "wrong": [label for label, _ in lesson["challenge"]["wrong"]],
                    "jsLang": lesson["challenge"]["js_lang"],
                    "jsOriginal": lesson["challenge"]["js_original"],
                    "jsChecks": lesson["challenge"]["js_checks"],
                }} if lesson["kind"] == "runnable" else {}),
            }
    (HERE / "expectations.json").write_text(json.dumps(expectations, indent=2) + "\n",
                                            encoding="utf-8")
    print(f"Wrote {len(expectations)} lessons to {ROOT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
