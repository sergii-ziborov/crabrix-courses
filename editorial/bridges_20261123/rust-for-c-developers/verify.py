#!/usr/bin/env python3
"""Verify every claim the rust-for-c-developers lessons make about real compilers.

Run from anywhere:  python3 -I editorial/bridges_20261123/rust-for-c-developers/verify.py
Optional: --lesson <id> (repeatable) verifies only those lessons and does not
rewrite verification.json.

For each lesson this compiles and runs, with rustc 1.89.0 and 1.100.0
(edition 2024, debug profile):
  * writing.exampleCode, comparing stdout with the authored expectation and
    requiring zero warnings;
  * writing.practiceCode, asserting the exact rustc error codes, message or
    panic the lesson describes;
  * every recall card that has code, and the quiz probes;
and with clang (C17, -Wall -Wextra) the C fromCode, plus a sanitizer build
when the prose relies on a sanitizer finding.
For runnable lessons the packaged stub must compile and fail its harness, the
reference solution must print exactly expectedOutput in debug and release
builds and compile for wasm32-wasip1, and each recorded wrong port must be
rejected in debug and release builds.
"""

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
COURSE_ID = "rust-for-c-developers"
COURSE = REPO / "courses" / COURSE_ID
WORK = REPO / "build" / "bridges-20261123" / COURSE_ID
TOOLCHAINS = Path.home() / ".rustup" / "toolchains"
RUSTC = {
    "1.89.0": TOOLCHAINS / "1.89.0-aarch64-apple-darwin" / "bin" / "rustc",
    "1.100.0": TOOLCHAINS / "1.100.0-aarch64-apple-darwin" / "bin" / "rustc",
}
WASM_RUSTC = TOOLCHAINS / "stable-aarch64-apple-darwin" / "bin" / "rustc"
CLANG = "/usr/bin/clang"
STUB = 'todo!("implement the contract")'
ALLOWED_CREDIT_COURSES = {"basics", "ownership", "projects", "concurrency", "systems"}
ERROR_CODE = re.compile(r"error\[(E\d{4})\]")

sys.path.insert(0, str(HERE))


class Failure(Exception):
    pass


def need(condition: bool, message: str) -> None:
    if not condition:
        raise Failure(message)


def run(cmd, cwd=None, timeout=60, env=None):
    merged = dict(os.environ, **(env or {}))
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=merged)


def rust(source: str, folder: Path, version: str, extra: dict | None = None,
         release: bool = False, target: str | None = None) -> dict:
    """Compile main.rs (plus extra files) and run it. Returns a record."""
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    (folder / "main.rs").write_text(source, encoding="utf-8")
    for name, text in (extra or {}).items():
        (folder / name).write_text(text, encoding="utf-8")
    rustc = WASM_RUSTC if target else RUSTC[version]
    cmd = [str(rustc), "--edition=2024", "main.rs", "-o", "program"]
    if release:
        cmd[2:2] = ["-C", "opt-level=2"]
    if target:  # rust-lld cannot run on this Mac, so stop after code generation
        cmd = [str(rustc), "--edition=2024", "--target", target, "--emit=obj", "main.rs", "-o", "program.o"]
    built = run(cmd, cwd=folder, timeout=180)
    record = {"compiled": built.returncode == 0,
              "errors": sorted(set(ERROR_CODE.findall(built.stderr))),
              "warnings": built.stderr.count("warning:") if built.returncode == 0 else None}
    (folder / "rustc.log").write_text(built.stderr, encoding="utf-8")
    if built.returncode != 0:
        record["stderr"] = built.stderr
        return record
    if target:
        return record
    ran = run([str(folder / "program")], cwd=folder, timeout=60)
    record.update(exit=ran.returncode, stdout=ran.stdout, runStderr=ran.stderr)
    return record


def as_program(code: str) -> str:
    if "fn main()" in code:
        return code
    body = "\n".join(("    " + line) if line else "" for line in code.splitlines())
    return "fn main() {\n" + body + "\n}\n"


def outcome_matches(record: dict, expect: dict, what: str) -> None:
    if "errors" in expect or "message" in expect:
        need(not record["compiled"], f"{what}: expected a compile error, but it compiled")
        if "errors" in expect:
            need(record["errors"] == sorted(expect["errors"]),
                 f"{what}: error codes {record['errors']} != {expect['errors']}")
        if "message" in expect:
            need(expect["message"] in record["stderr"], f"{what}: missing message {expect['message']!r}")
        return
    need(record["compiled"], f"{what}: did not compile:\n{record.get('stderr', '')[:2500]}")
    if "panic" in expect:
        need(record["exit"] == 101, f"{what}: expected a panic, exit {record['exit']}")
        need(expect["panic"] in record["runStderr"], f"{what}: panic text {record['runStderr']!r}")
        if "stdout" in expect:
            need(record["stdout"] == expect["stdout"], f"{what}: stdout {record['stdout']!r}")
        return
    if expect.get("compiles"):
        return
    need(record["exit"] == 0, f"{what}: exit {record['exit']} stderr {record['runStderr'][:800]}")
    need(record["stdout"] == expect["stdout"],
         f"{what}: stdout\n{record['stdout']!r}\n!= expected\n{expect['stdout']!r}")


def prose_fields(lesson: dict) -> list[str]:
    w, d, b = lesson["writing"], lesson["depth"], lesson["bridge"]
    fields = [w[k] for k in ("summary", "explanation", "rule", "task", "success", "question",
                             "feedback", "exampleCaption")]
    fields += [d[k] for k in ("misconception", "correction", "transferChallenge")]
    fields += [s["detail"] for s in d["traceSteps"]] + [s["title"] for s in d["traceSteps"]]
    fields += list(w["answers"]) + [b["fromCaption"]]
    fields += [row[k] for row in b["contrasts"] for k in ("from", "rust")]
    fields += [card[k] for card in w["recall"] for k in ("question", "answer")]
    return fields


def check_fields(lesson: dict, check: dict) -> None:
    lid = lesson["id"]
    need(lid.startswith("c-"), "id prefix")
    need(8 <= lesson["minutes"] <= 14, "minutes")
    need(lesson["exerciseKind"] in {"runnable", "planned"}, "exerciseKind")
    w, d, b = lesson["writing"], lesson["depth"], lesson["bridge"]
    required = {"summary", "explanation", "exampleCaption", "exampleCode", "task", "success", "rule",
                "practiceCode", "question", "answers", "correctAnswer", "feedback", "recall"}
    need(set(w) == required, f"writing keys {sorted(set(w) ^ required)}")
    need(len(w["explanation"].split("\n\n")) >= 3, "explanation needs at least 3 paragraphs")
    need(3 <= len(w["answers"]) <= 4 and 0 <= w["correctAnswer"] < len(w["answers"]), "answers")
    need(len(set(w["answers"])) == len(w["answers"]), "duplicate answers")
    need(len(w["recall"]) == 2, "exactly two recall cards")
    for card in w["recall"]:
        need(set(card) <= {"question", "answer", "code"}, "recall keys")
        need("core idea" not in card["question"].lower(), "recall wording")
        need(len(card["answer"]) <= 600, "recall answer length")
        need(len(card.get("code", "").splitlines()) <= 16, "recall code length")
    need(set(d) == {"traceSteps", "misconception", "correction", "transferChallenge", "connections"},
         "depth keys")
    need(len(d["traceSteps"]) == 3, "three trace steps")
    need(1 <= len(d["connections"]) <= 2, "connections")
    for connection in d["connections"]:
        need(connection["direction"] in {"previous", "next"}, "connection direction")
    need(set(b) == {"from", "fromLabel", "fromCode", "fromCaption", "contrasts", "credits"}, "bridge keys")
    need(b["from"] == "c" and b["fromLabel"] == "C", "bridge language")
    need(len(b["fromCode"].splitlines()) <= 30, "fromCode length")
    need(2 <= len(b["contrasts"]) <= 4, "contrast count")
    for row in b["contrasts"]:
        need(set(row) == {"from", "rust"} and all(len(row[k]) <= 160 for k in row), "contrast row")
    need(1 <= len(b["credits"]) <= 4, "credit count")
    for target in b["credits"]:
        course, target_id = target.split("/")
        need(course in ALLOWED_CREDIT_COURSES, f"credit course {target}")
        need((REPO / "courses" / course / "lessons" / f"{target_id}.json").exists(),
             f"credit target missing {target}")
    need("fn main()" in w["exampleCode"], "example must be a complete program")
    for text in prose_fields(lesson):
        need(text.count("`") % 2 == 0, f"odd backticks in {text[:70]!r}")
    if lesson["exerciseKind"] == "planned":
        need(check == {"evidence": {"correctAnswer": w["correctAnswer"], "kind": "reasoning"}},
             "reasoning evidence")
    else:
        need(check["evidence"]["kind"] == "algorithmChallenge", "challenge evidence")
        need(len(check["challenge"]["verificationCases"]) >= 3, "at least three verification cases")
        kinds = {case["kind"] for case in check["challenge"]["verificationCases"]}
        need({"visible", "boundary", "semantic"} <= kinds, f"case kinds {kinds}")


def check_c(lid: str, code: str, expect: dict, folder: Path) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "from.c").write_text(code, encoding="utf-8")
    built = run([CLANG, "-std=c17", "-Wall", "-Wextra", "-O0", "from.c", "-o", "from"], cwd=folder)
    need(built.returncode == 0, f"{lid}: C did not compile\n{built.stderr}")
    warnings = sorted(set(re.findall(r"\[(-W[a-z0-9-]+)\]", built.stderr)))
    need(warnings == sorted(expect.get("warnings", [])), f"{lid}: C warnings {warnings}")
    record = {"compiler": run([CLANG, "--version"]).stdout.splitlines()[0], "warnings": warnings}
    ran = run([str(folder / "from")], cwd=folder)
    record.update(exit=ran.returncode, stdout=ran.stdout)
    if "stdout" in expect:
        need(ran.stdout == expect["stdout"], f"{lid}: C stdout {ran.stdout!r}")
    if "stdoutPrefix" in expect:
        need(ran.stdout.startswith(expect["stdoutPrefix"]), f"{lid}: C stdout {ran.stdout!r}")
    if "exit" in expect:
        need(ran.returncode == expect["exit"], f"{lid}: C exit {ran.returncode}")
    if "sanitize" in expect:
        flags = ["-fsanitize=" + expect["sanitize"], "-g", "-O0", "-fno-omit-frame-pointer"]
        sanitized = run([CLANG, "-std=c17", *flags, "from.c", "-o", "from-sanitized"], cwd=folder)
        need(sanitized.returncode == 0, f"{lid}: sanitizer build failed\n{sanitized.stderr}")
        result = run([str(folder / "from-sanitized")], cwd=folder, timeout=120,
                     env={"ASAN_OPTIONS": "detect_leaks=0", "TSAN_OPTIONS": "halt_on_error=0"})
        (folder / "sanitizer.log").write_text(result.stderr, encoding="utf-8")
        need(expect["finding"] in result.stderr, f"{lid}: sanitizer finding missing\n{result.stderr[:2000]}")
        line = next(l for l in result.stderr.splitlines() if expect["finding"] in l)
        record["sanitizer"] = {"flags": expect["sanitize"], "finding": re.sub(r"0x[0-9a-f]+", "0x…", line.strip())}
    return record


def check_challenge(lid: str, check: dict, expect: dict) -> dict:
    challenge = check["challenge"]
    harness = challenge["verificationSource"]
    expected = challenge["expectedOutput"]
    stub = (COURSE / "projects" / lid / "solution.rs").read_text(encoding="utf-8")
    need(stub == challenge["source"], "project stub differs from challenge.source")
    need(STUB in stub, "stub must contain the forbidden todo! fragment")
    need(json.loads((COURSE / "projects" / lid / "project.json").read_text())
         == {"name": challenge["projectName"], "entryFile": "solution.rs"}, "project.json")
    reference = (HERE / "solutions" / f"{lid}.rs").read_text(encoding="utf-8")
    for fragment in challenge["requiredSourceFragments"]:
        need(fragment in reference and fragment in stub, f"required fragment {fragment!r}")
    for fragment in challenge["forbiddenSourceFragments"]:
        need(fragment not in reference, f"forbidden fragment in reference {fragment!r}")
    record = {"cases": len(challenge["verificationCases"]), "stub": {}, "reference": {}, "wrong": {}}
    base = WORK / lid / "challenge"
    for version in RUSTC:
        r = rust(harness, base / f"stub-{version}", version, {"solution.rs": stub})
        need(r["compiled"], f"stub + harness must compile with {version}:\n{r.get('stderr', '')[:2000]}")
        need(r["exit"] != 0 and r["stdout"] != expected, "stub must fail the harness")
        record["stub"][version] = "compiled, failed"
        r = rust(harness, base / f"reference-{version}", version, {"solution.rs": reference})
        need(r["compiled"] and r["exit"] == 0 and r["stdout"] == expected,
             f"reference must pass with {version}: {r}")
        record["reference"][version] = "passed"
    r = rust(harness, base / "reference-release", "1.100.0", {"solution.rs": reference}, release=True)
    need(r["compiled"] and r["exit"] == 0 and r["stdout"] == expected, f"reference release: {r}")
    record["reference"]["1.100.0 release"] = "passed"
    r = rust(harness, base / "reference-wasm", "stable", {"solution.rs": reference}, target="wasm32-wasip1")
    need(r["compiled"], f"reference must compile for wasm32-wasip1:\n{r.get('stderr', '')[:2000]}")
    record["reference"]["wasm32-wasip1 (rustc 1.99.0)"] = "compiled to an object file (not linked)"
    wrong_files = sorted((HERE / "wrong").glob(f"{lid}.*.rs"))
    need(wrong_files, "at least one wrong port")
    declared = expect.get("wrong", {})
    need(set(declared) == {p.name for p in wrong_files}, f"wrong-port expectations {sorted(declared)}")
    for path in wrong_files:
        source = path.read_text(encoding="utf-8")
        modes = {}
        for label, version, release in (("1.89.0", "1.89.0", False), ("1.100.0", "1.100.0", False),
                                        ("1.100.0 release", "1.100.0", True)):
            r = rust(harness, base / f"wrong-{path.stem}-{label.replace(' ', '-')}", version,
                     {"solution.rs": source}, release=release)
            if not r["compiled"]:
                mode = "compile error " + ",".join(r["errors"])
            elif r["exit"] != 0:
                mode = "panic" if r["exit"] == 101 else f"exit {r['exit']}"
            else:
                need(r["stdout"] != expected, f"wrong port {path.name} passed with {label}")
                mode = "wrong output"
            modes[label] = mode
        want = declared[path.name]
        for label, mode in modes.items():
            need(mode.startswith(want.get(label, want["mode"])),
                 f"{path.name} {label}: rejected as {mode!r}, expected {want}")
        record["wrong"][path.name] = {"note": want["note"], "rejected": modes}
    return record


def verify_lesson(module, lesson: dict, check: dict) -> dict:
    lid = lesson["id"]
    expect = module.EXPECT
    check_fields(lesson, check)
    w = lesson["writing"]
    record = {"id": lid, "exerciseKind": lesson["exerciseKind"], "credits": lesson["bridge"]["credits"],
              "example": {}, "practice": {}, "recall": {}, "probes": {}}
    folder = WORK / lid
    for version in RUSTC:
        r = rust(w["exampleCode"], folder / f"example-{version}", version)
        outcome_matches(r, {"stdout": expect["example"]}, f"{lid} example ({version})")
        need(r["warnings"] == 0, f"{lid} example has warnings with {version}:\n"
             + (folder / f"example-{version}" / "rustc.log").read_text())
        record["example"][version] = "compiled without warnings, stdout matched"
        r = rust(w["practiceCode"], folder / f"practice-{version}", version)
        outcome_matches(r, expect["practice"], f"{lid} practice ({version})")
        record["practice"][version] = expect["practice"]
        recall_expect = expect.get("recall", [None, None])
        need(len(recall_expect) == len(w["recall"]), "recall expectations")
        for index, (card, card_expect) in enumerate(zip(w["recall"], recall_expect)):
            if "code" not in card:
                need(card_expect is None, f"recall {index} has no code")
                continue
            need(card_expect is not None, f"recall {index} needs an expectation")
            r = rust(as_program(card["code"]), folder / f"recall{index}-{version}", version)
            outcome_matches(r, card_expect, f"{lid} recall {index} ({version})")
            record["recall"][f"{index} {version}"] = card_expect
        for name, probe in expect.get("probes", {}).items():
            r = rust(as_program(probe["code"]), folder / f"probe-{name}-{version}", version)
            outcome_matches(r, probe, f"{lid} probe {name} ({version})")
            record["probes"][f"{name} {version}"] = {k: v for k, v in probe.items() if k != "code"}
    if "cargo" in expect:
        record["cargo"] = check_cargo(lid, expect["cargo"])
    record["c"] = check_c(lid, lesson["bridge"]["fromCode"], expect["c"], folder / "c")
    if lesson["exerciseKind"] == "runnable":
        record["challenge"] = check_challenge(lid, check, expect)
    return record


def check_cargo(lid: str, spec: dict) -> dict:
    folder = WORK / lid / "cargo" / spec["package"]
    if folder.exists():
        shutil.rmtree(folder)
    for name, text in spec["files"].items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    cargo = TOOLCHAINS / "1.100.0-aarch64-apple-darwin" / "bin" / "cargo"
    env = {"RUSTC": str(RUSTC["1.100.0"]), "CARGO_TARGET_DIR": str(folder / "target")}
    result = run([str(cargo), "run", "--quiet", "--offline"], cwd=folder, timeout=300, env=env)
    if "stdout" in spec:
        need(result.returncode == 0 and result.stdout == spec["stdout"],
             f"{lid} cargo: {result.returncode} {result.stdout!r} {result.stderr[:1500]}")
    if "errors" in spec:
        need(result.returncode != 0 and sorted(set(ERROR_CODE.findall(result.stderr))) == spec["errors"],
             f"{lid} cargo expected {spec['errors']}: {result.stderr[:1500]}")
    return {k: v for k, v in spec.items() if k != "files"}


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lesson", action="append")
    args = parser.parse_args()
    course = json.loads((COURSE / "course.json").read_text(encoding="utf-8"))
    modules = {m.ID: m for m in map(load_module, sorted((HERE / "lessons_src").glob("*.py")))}
    order = [lid for uid in course["unitIDs"]
             for lid in json.loads((COURSE / "units" / f"{uid}.json").read_text())["lessonIDs"]]
    need(set(order) == set(modules), "author.py output is stale: run author.py")
    selected = args.lesson or order
    records, failures = [], []
    seen_targets: dict[str, str] = {}
    for lid in order:
        lesson = json.loads((COURSE / "lessons" / f"{lid}.json").read_text(encoding="utf-8"))
        for target in lesson["bridge"]["credits"]:
            need(target not in seen_targets, f"{target} credited twice ({seen_targets.get(target)}, {lid})")
            seen_targets[target] = lid
        if lid not in selected:
            continue
        check = json.loads((COURSE / "checks" / f"{lid}.json").read_text(encoding="utf-8"))
        try:
            records.append(verify_lesson(modules[lid], lesson, check))
            print(f"ok   {lid}")
        except Failure as error:
            failures.append(lid)
            print(f"FAIL {lid}: {error}")
    if failures:
        raise SystemExit(f"{len(failures)} lesson(s) failed: {', '.join(failures)}")
    lessons = [json.loads((COURSE / "lessons" / f"{lid}.json").read_text()) for lid in order]
    positions = [lesson["writing"]["correctAnswer"] for lesson in lessons]
    runnable = sum(lesson["exerciseKind"] == "runnable" for lesson in lessons)
    summary = {"lessons": len(order), "runnable": runnable,
               "correctAnswerPositions": positions, "credits": len(seen_targets)}
    if not args.lesson:
        need(len(set(positions)) >= 3, "correct answer positions must vary")
        need(runnable / len(order) >= 0.6, "at least 60% runnable lessons")
        counts = {}
        for record in records:
            for version in RUSTC:
                c = counts.setdefault(version, {"compiledAndRan": 0, "expectedCompileErrors": 0,
                                                "expectedPanics": 0, "wrongPortsRejected": 0})
                c["compiledAndRan"] += 1  # example
                practice = record["practice"][version]
                c["expectedCompileErrors" if ("errors" in practice or "message" in practice)
                  else "expectedPanics"] += 1
                for key, value in record["recall"].items():
                    if key.endswith(version):
                        c["expectedCompileErrors" if "errors" in value else
                          "expectedPanics" if "panic" in value else "compiledAndRan"] += 1
                for key, value in record["probes"].items():
                    if key.endswith(version):
                        c["expectedCompileErrors" if "errors" in value else "compiledAndRan"] += 1
                if "challenge" in record:
                    c["compiledAndRan"] += 2  # stub (fails) and reference (passes)
                    c["wrongPortsRejected"] += len(record["challenge"]["wrong"])
        summary["perToolchain"] = counts
        summary["cPrograms"] = len(records)
        summary["sanitizerFindings"] = sum("sanitizer" in r["c"] for r in records)
        out = {"course": COURSE_ID, "rustc": {v: run([str(p), "--version"]).stdout.strip()
                                              for v, p in RUSTC.items()},
               "wasmRustc": run([str(WASM_RUSTC), "--version"]).stdout.strip(),
               "clang": run([CLANG, "--version"]).stdout.splitlines()[0],
               "summary": summary, "lessons": records}
        (HERE / "verification.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                                               encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
