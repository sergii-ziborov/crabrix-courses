#!/usr/bin/env python3
"""Qualify Playground practice copies for lessons that have no starter project.

Writes academy/practice-starters.json (docs/ai-learning/PLAN.md, "Phase 4"). A lesson is
listed only when one of its own fields, unchanged, is a whole program that the browser
Playground's compiler target accepts:

* practiceCode that compiles -> source "practiceCode", check "compiles";
* else exampleCode that compiles -> source "exampleCode", check "compiles";
* practiceCode that does not compile is listed as "fails-by-design" only when the lesson's
  exercise is to repair code (exerciseKind borrowDiagnostic / repair). Otherwise it is skipped.
* a field without `fn main` is placed, unchanged, into a program: definitions get an empty
  `fn main() {}` appended (wrap "main-added"), statements are indented into `fn main` (wrap
  "in-main"). `program()` is the one implementation; the site applies the same transform and
  checks programSha256.

Lessons with their own playgroundProject (or Algorithm Atlas steps) keep their existing
Playground behaviour and are not listed. Grading harnesses and checks are never read.

Usage: tools/practice_starters.py [--check]   (--check: fail if the file is out of date)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "academy" / "practice-starters.json"
COURSES = ["basics", "ownership", "concurrency", "systems", "projects", "interview",
           "rust-for-c-developers", "rust-for-nodejs-developers"]
# Lessons whose site starter is set by site/scripts/sync-course-content.py (qualified there).
SITE_PROJECT_LESSONS = {"public-api-compatibility", "msrv-verification", "feature-compatibility-matrix",
                        "serde-roundtrip-validation", "joinset-task-ownership", "semaphore-backpressure",
                        "graceful-shutdown-protocol", "async-runtime"}
REPAIR_KINDS = {"borrowDiagnostic", "repair"}
TARGET = "wasm32-wasip1"
EDITION = "2024"


def rustc() -> str:
    found = os.environ.get("RUSTC") or shutil.which("rustc") or str(Path.home() / ".cargo" / "bin" / "rustc")
    if not Path(found).exists() and not shutil.which(found):
        sys.exit("rustc not found; set RUSTC")
    return found


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compiles(compiler: str, code: str) -> bool:
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder) / "main.rs"
        source.write_text(code, encoding="utf-8")
        result = subprocess.run(
            [compiler, "--edition", EDITION, "--target", TARGET, "--crate-type", "bin", "--crate-name", "practice",
             "--emit=metadata", "-o", str(Path(folder) / "out.rmeta"), "--cap-lints", "allow", str(source)],
            capture_output=True, text=True, timeout=120)
        return result.returncode == 0


def is_program(code: str) -> bool:
    return "fn main" in code and len(code.encode("utf-8")) <= 64 * 1024


def program(code: str, wrap: str | None) -> str:
    """The Playground file for a lesson field. Must match site/lib/practice-copy.ts."""
    if wrap is None:
        return code
    body = code.rstrip()
    if wrap == "main-added":
        return body + "\n\nfn main() {}\n"
    if wrap == "in-main":
        return "fn main() {\n" + "\n".join(("    " + line) if line else line for line in body.split("\n")) + "\n}\n"
    raise ValueError(wrap)


def lessons():
    for course_id in COURSES:
        folder = ROOT / "courses" / course_id
        if not (folder / "course.json").is_file():
            continue
        course = json.loads((folder / "course.json").read_text(encoding="utf-8"))
        for unit_id in course["unitIDs"]:
            unit = json.loads((folder / "units" / f"{unit_id}.json").read_text(encoding="utf-8"))
            for lesson_id in unit["lessonIDs"]:
                lesson = json.loads((folder / "lessons" / f"{lesson_id}.json").read_text(encoding="utf-8"))
                if lesson.get("playgroundProject") or lesson_id in SITE_PROJECT_LESSONS:
                    continue
                if course_id == "projects" and lesson_id.startswith("route-"):
                    continue
                yield course_id, lesson


def qualify(compiler: str, course_id: str, lesson: dict) -> dict | None:
    writing = lesson.get("writing") or {}
    entry = {"courseId": course_id, "lessonId": lesson["id"], "edition": EDITION}

    def listed(field: str, wrap: str | None, check: str) -> dict:
        code = writing[field]
        return {**entry, "source": field, "wrap": wrap, "sha256": sha256(code),
                "programSha256": sha256(program(code, wrap)), "check": check}

    practice, example = writing.get("practiceCode") or "", writing.get("exampleCode") or ""
    if is_program(practice):
        if compiles(compiler, practice):
            return listed("practiceCode", None, "compiles")
        if lesson.get("exerciseKind") in REPAIR_KINDS:
            return listed("practiceCode", None, "fails-by-design")
    if is_program(example) and compiles(compiler, example):
        return listed("exampleCode", None, "compiles")
    for field, code in (("practiceCode", practice), ("exampleCode", example)):
        if not code.strip() or "fn main" in code or len(code.encode("utf-8")) > 60 * 1024:
            continue
        for wrap in ("main-added", "in-main"):
            if compiles(compiler, program(code, wrap)):
                return listed(field, wrap, "compiles")
    return None


def build() -> dict:
    compiler = rustc()
    version = subprocess.run([compiler, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    work = list(lessons())
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        results = list(pool.map(lambda item: qualify(compiler, *item), work))
    starters = sorted((item for item in results if item), key=lambda item: (COURSES.index(item["courseId"]), item["lessonId"]))
    return {
        "schemaVersion": 1,
        "checkedWith": f"{version.split(' (')[0]}, --target {TARGET} --edition {EDITION}, check only",
        "considered": len(work),
        "starters": starters,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    payload = build()
    text = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"
    if arguments.check:
        current = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if current["starters"] != payload["starters"]:
            sys.exit("academy/practice-starters.json is out of date: run tools/practice_starters.py")
        print(f"practice starters up to date: {len(payload['starters'])}")
        return
    OUTPUT.write_text(text, encoding="utf-8")
    counts: dict[str, int] = {}
    for item in payload["starters"]:
        key = f"{item['source']}:{item['wrap'] or 'whole'}:{item['check']}"
        counts[key] = counts.get(key, 0) + 1
    print(f"{OUTPUT.relative_to(ROOT)}: {len(payload['starters'])} of {payload['considered']} lessons {counts}")


if __name__ == "__main__":
    main()
