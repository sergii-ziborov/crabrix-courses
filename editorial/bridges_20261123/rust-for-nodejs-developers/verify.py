#!/usr/bin/env python3
"""Verify rust-for-nodejs-developers against SPEC.md and write verification.json.

Run: python3 -I editorial/bridges_20261123/rust-for-nodejs-developers/verify.py [lesson-id ...]

For every lesson it compiles and runs the Rust example with rustc 1.89.0 and
1.100.0, compiles the practice code and recall snippets and checks the outcome
the prose describes, runs the JavaScript or TypeScript side (tsc --strict, then
node), and for runnable lessons proves that the starter fails, the reference
solution passes the packaged harness exactly and every recorded wrong port is
rejected. The JavaScript original of each lab is run on the same cases.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
COURSE_ID = "rust-for-nodejs-developers"
ROOT = REPO / "courses" / COURSE_ID
WORK = REPO / "build" / "bridges-20261123" / COURSE_ID
HOME = Path.home()
RUSTC = {
    "1.89.0": HOME / ".rustup/toolchains/1.89.0-aarch64-apple-darwin/bin/rustc",
    "1.100.0": HOME / ".rustup/toolchains/1.100.0-aarch64-apple-darwin/bin/rustc",
}
NODE = "node"
SITE_MODULES = Path("/Users/serhiirihgt/dev/crabrix-poc/site/node_modules")
TSC = SITE_MODULES / ".bin" / "tsc"
TODO = 'todo!("implement the contract")'
CREDIT_COURSES = {"basics", "ownership", "projects", "concurrency", "systems"}
PROSE_WRITING = ("summary", "explanation", "rule", "task", "success", "question", "feedback", "exampleCaption")
PROSE_DEPTH = ("misconception", "correction", "transferChallenge")

failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)
    print("FAIL", message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run(args, cwd=None, timeout=60, env=None):
    return subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, env=env)


def codes(stderr: str) -> list[str]:
    return sorted(set(re.findall(r"error\[(E\d{4})\]", stderr)))


def compile_rust(source: str, directory: Path, version: str, main_name="main.rs"):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / main_name).write_text(source, encoding="utf-8")
    binary = directory / f"bin-{version}"
    if binary.exists():
        binary.unlink()
    result = run([RUSTC[version], "--edition=2024", "-o", binary, directory / main_name], cwd=directory)
    return result, binary


def outcome(source: str, directory: Path, expect: dict, label: str) -> dict:
    """Compile (and run, if it builds) with both compilers and compare to expect."""
    record = {}
    for version in RUSTC:
        result, binary = compile_rust(source, directory / version, version)
        entry = {"compiled": result.returncode == 0, "errorCodes": codes(result.stderr)}
        stderr = result.stderr
        if result.returncode == 0:
            ran = run([binary], cwd=directory)
            entry.update(exitCode=ran.returncode, stdout=ran.stdout)
            stderr += ran.stderr
            if ran.returncode != 0:
                entry["runtimeError"] = panic_text(ran.stderr)
        record[version] = entry
        if "stdout" in expect:
            if result.returncode != 0:
                fail(f"{label} [{version}] does not compile: {result.stderr[:400]}")
            elif entry.get("exitCode") != 0 or entry.get("stdout") != expect["stdout"]:
                fail(f"{label} [{version}] stdout {entry.get('stdout')!r} != {expect['stdout']!r}")
            for warning in expect.get("warnings", []):
                if warning not in result.stderr:
                    fail(f"{label} [{version}] missing warning {warning!r}")
        elif "panic" in expect:
            if result.returncode != 0:
                fail(f"{label} [{version}] should compile and panic: {result.stderr[:400]}")
            elif entry.get("exitCode") == 0 or expect["panic"] not in stderr:
                fail(f"{label} [{version}] expected panic containing {expect['panic']!r}, got {stderr[-400:]!r}")
            if "stdout" in expect.get("panicStdout", {}):
                pass
        else:
            if result.returncode == 0:
                fail(f"{label} [{version}] compiled but should fail")
            for code in expect.get("errors", []):
                if code not in entry["errorCodes"]:
                    fail(f"{label} [{version}] missing {code}; found {entry['errorCodes']}")
            for message in expect.get("messages", []):
                if message not in result.stderr:
                    fail(f"{label} [{version}] missing message {message!r}")
    return record


def wrap(snippet: str) -> str:
    if "fn main(" in snippet:
        return snippet + "\n"
    body = "\n".join("    " + line if line else "" for line in snippet.splitlines())
    return f"#[allow(unused)]\nfn main() {{\n{body}\n}}\n"


def check_fields(course, units, lessons, checks, terms) -> None:
    unit_ids = course["unitIDs"]
    if not 3 <= len(unit_ids) <= 4:
        fail("unit count")
    seen_credits = {}
    corrects = []
    all_lessons = {p.stem: p.parent.parent.name for p in (REPO / "courses").glob("*/lessons/*.json")}
    for unit_order, uid in enumerate(unit_ids):
        unit = units[uid]
        if unit["order"] != unit_order or unit["parentID"] != COURSE_ID or not 3 <= len(unit["lessonIDs"]) <= 6:
            fail(f"unit {uid} identity or size")
        for order, lid in enumerate(unit["lessonIDs"]):
            lesson = lessons.get(lid)
            if lesson is None:
                fail(f"missing lesson {lid}")
                continue
            w, d, b = lesson["writing"], lesson["depth"], lesson["bridge"]
            label = lid
            if not lid.startswith("node-") or lesson["parentID"] != uid or lesson["order"] != order:
                fail(f"{label}: id/parent/order")
            if not 8 <= lesson["minutes"] <= 14:
                fail(f"{label}: minutes")
            for key in PROSE_WRITING + ("exampleCode", "practiceCode"):
                if not str(w.get(key, "")).strip():
                    fail(f"{label}: writing.{key} missing")
            if len(w["explanation"].split("\n\n")) < 2:
                fail(f"{label}: explanation needs paragraphs")
            if not 3 <= len(w["answers"]) <= 4 or not 0 <= w["correctAnswer"] < len(w["answers"]):
                fail(f"{label}: answers")
            corrects.append(w["correctAnswer"])
            if len(w.get("recall", [])) != 2:
                fail(f"{label}: recall must have exactly 2 cards")
            for card in w.get("recall", []):
                if set(card) - {"question", "answer", "code"} or len(card["answer"]) > 600 \
                        or "core idea" in card["question"].lower() \
                        or len(card.get("code", "").splitlines()) > 16:
                    fail(f"{label}: recall card rules")
            if len(d["traceSteps"]) != 3 or not 1 <= len(d["connections"]) <= 2:
                fail(f"{label}: depth sizes")
            for conn in d["connections"]:
                if conn["direction"] not in ("previous", "next"):
                    fail(f"{label}: connection direction")
            prose = [w[k] for k in PROSE_WRITING] + [d[k] for k in PROSE_DEPTH]
            prose += [s["detail"] for s in d["traceSteps"]] + [s["title"] for s in d["traceSteps"]]
            prose += [c["question"] for c in w["recall"]] + [c["answer"] for c in w["recall"]]
            prose += [b["fromCaption"]] + w["answers"]
            for field in prose:
                if field.count("`") % 2:
                    fail(f"{label}: odd backticks in {field[:60]!r}")
            if "fn main()" not in w["exampleCode"]:
                fail(f"{label}: example needs fn main")
            if b["from"] not in ("javascript", "typescript") or len(b["fromCode"].splitlines()) > 30:
                fail(f"{label}: bridge language/length")
            if not 2 <= len(b["contrasts"]) <= 4:
                fail(f"{label}: contrasts count")
            for row in b["contrasts"]:
                for key in ("from", "rust"):
                    if len(row[key]) > 160 or row[key].count("`") % 2:
                        fail(f"{label}: contrast cell {row[key][:50]!r}")
            if not 1 <= len(b["credits"]) <= 4:
                fail(f"{label}: credits count")
            for target in b["credits"]:
                course_id, _, target_lesson = target.partition("/")
                if course_id not in CREDIT_COURSES or all_lessons.get(target_lesson) != course_id:
                    fail(f"{label}: credit target {target} does not exist")
                if target in seen_credits:
                    fail(f"{label}: {target} already credited by {seen_credits[target]}")
                seen_credits[target] = lid
            check = checks[lid]
            if lesson["exerciseKind"] == "planned":
                if check != {"evidence": {"kind": "reasoning", "correctAnswer": w["correctAnswer"]}}:
                    fail(f"{label}: reasoning evidence")
            elif lesson["exerciseKind"] == "runnable":
                ch = check["challenge"]
                if check["evidence"]["kind"] != "algorithmChallenge" or ch["lessonID"] != lid \
                        or len(ch["verificationCases"]) < 3 \
                        or {c["kind"] for c in ch["verificationCases"]} < {"visible", "boundary", "semantic"}:
                    fail(f"{label}: challenge shape")
                project = ROOT / "projects" / lid
                if (project / "solution.rs").read_text(encoding="utf-8") != ch["source"] or TODO not in ch["source"]:
                    fail(f"{label}: starter differs from challenge.source")
                if load(project / "project.json") != {"name": ch["projectName"], "entryFile": "solution.rs"}:
                    fail(f"{label}: project.json")
            else:
                fail(f"{label}: exerciseKind {lesson['exerciseKind']}")
    if len(set(corrects)) < 2:
        fail("correctAnswer positions do not vary")
    runnable = sum(1 for l in lessons.values() if l["exerciseKind"] == "runnable")
    if lessons and runnable / len(lessons) < 0.6:
        fail(f"only {runnable}/{len(lessons)} runnable")
    if not 8 <= len(terms) <= 16 or any(t["topic"] not in lessons for t in terms):
        fail("terms")


def run_from(lid: str, lesson: dict, spec: dict, work: Path) -> dict:
    bridge = lesson["bridge"]
    work.mkdir(parents=True, exist_ok=True)
    record = {"lang": bridge["from"]}
    if "runner" in spec:
        (work / "from.json").write_text(bridge["fromCode"], encoding="utf-8")
        (work / "runner.cjs").write_text(spec["runner"], encoding="utf-8")
        env = dict(os.environ, NODE_PATH=str(SITE_MODULES))
        result = run([NODE, "runner.cjs", "from.json"], cwd=work, env=env)
    elif bridge["from"] == "typescript":
        (work / "from.ts").write_text(bridge["fromCode"] + "\n", encoding="utf-8")
        tsc = run([TSC, "--strict", "--noEmit", "--target", "es2022", "--module", "nodenext", "from.ts"], cwd=work)
        record["tsc"] = tsc.returncode
        if tsc.returncode:
            fail(f"{lid}: tsc rejects fromCode: {tsc.stdout[:600]}")
        result = run([NODE, "--experimental-strip-types", "--no-warnings", "from.ts"], cwd=work)
    else:
        (work / "from.js").write_text(bridge["fromCode"] + "\n", encoding="utf-8")
        result = run([NODE, "from.js"], cwd=work)
    record.update(exitCode=result.returncode, stdout=result.stdout)
    if result.returncode != 0 or result.stdout != spec["stdout"]:
        fail(f"{lid}: fromCode stdout {result.stdout!r} != {spec['stdout']!r} {result.stderr[:300]}")
    return record


def run_js_checks(lid: str, spec: dict, work: Path) -> dict:
    work.mkdir(parents=True, exist_ok=True)
    expressions = ",\n".join(expr for expr, _ in spec["jsChecks"])
    program = spec["jsOriginal"] + f"\n\nconsole.log(JSON.stringify([\n{expressions}\n]));\n"
    if spec["jsLang"] == "typescript":
        (work / "original.ts").write_text(program, encoding="utf-8")
        tsc = run([TSC, "--strict", "--noEmit", "--target", "es2022", "--module", "nodenext", "original.ts"], cwd=work)
        if tsc.returncode:
            fail(f"{lid}: tsc rejects lab original: {tsc.stdout[:600]}")
        result = run([NODE, "--experimental-strip-types", "--no-warnings", "original.ts"], cwd=work)
    else:
        (work / "original.js").write_text(program, encoding="utf-8")
        result = run([NODE, "original.js"], cwd=work)
    expected = [value for _, value in spec["jsChecks"]]
    try:
        actual = json.loads(result.stdout)
    except json.JSONDecodeError:
        actual = None
    if actual != expected:
        fail(f"{lid}: JavaScript original gives {actual!r}, expected {expected!r} {result.stderr[:300]}")
    return {"cases": len(expected), "matches": actual == expected}


def fragments_ok(source: str, check: dict) -> bool:
    ch = check["challenge"]
    return all(f in source for f in ch["requiredSourceFragments"]) and \
        not any(f in source for f in ch["forbiddenSourceFragments"])


def panic_text(stderr: str) -> list[str]:
    lines = stderr.strip().splitlines()
    for index, line in enumerate(lines):
        if "panicked at" in line:
            return lines[index:index + 2]
    return lines[-1:]


def run_lab(source: str, harness: str, directory: Path, version: str):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "solution.rs").write_text(source, encoding="utf-8")
    result, binary = compile_rust(harness, directory, version)
    if result.returncode != 0:
        return {"compiled": False, "errorCodes": codes(result.stderr)}
    ran = run([binary], cwd=directory)
    return {"compiled": True, "exitCode": ran.returncode, "stdout": ran.stdout,
            "panic": panic_text(ran.stderr) if ran.returncode else []}


def verify_lab(lid: str, check: dict, spec: dict, work: Path) -> dict:
    ch = check["challenge"]
    expected = ch["expectedOutput"]
    record = {"stub": {}, "reference": {}, "wrong": []}
    for version in RUSTC:
        stub = run_lab(ch["source"], ch["verificationSource"], work / "stub" / version, version)
        record["stub"][version] = stub
        if stub.get("compiled") and stub.get("exitCode") == 0 and stub.get("stdout") == expected:
            fail(f"{lid}: starter passes the harness [{version}]")
        reference_source = (HERE / "solutions" / f"{lid}.rs").read_text(encoding="utf-8")
        reference = run_lab(reference_source, ch["verificationSource"], work / "reference" / version, version)
        record["reference"][version] = reference
        if not reference.get("compiled") or reference.get("exitCode") != 0 or reference.get("stdout") != expected:
            fail(f"{lid}: reference fails [{version}]: {reference}")
        if not fragments_ok(reference_source, check):
            fail(f"{lid}: reference violates source fragments")
    wrong_dir = HERE / "wrong" / lid
    labels = spec["wrong"]
    if not labels:
        fail(f"{lid}: no wrong port recorded")
    for index, label in enumerate(labels, start=1):
        source = (wrong_dir / f"{index}.rs").read_text(encoding="utf-8")
        outcomes = {}
        for version in RUSTC:
            result = run_lab(source, ch["verificationSource"], work / "wrong" / str(index) / version, version)
            if not result["compiled"]:
                reason = f"does not compile ({', '.join(result['errorCodes']) or 'error'})"
            elif result["exitCode"] != 0:
                reason = f"harness fails: {' '.join(result['panic'])}"
            elif result["stdout"] != expected:
                reason = "wrong output"
            elif not fragments_ok(source, check):
                reason = "rejected by source fragments"
            else:
                reason = None
                fail(f"{lid}: wrong port {label!r} is accepted [{version}]")
            outcomes[version] = reason
        record["wrong"].append({"label": label, "rejectedBy": outcomes})
    record["javascriptOriginal"] = run_js_checks(lid, spec, work / "js")
    return record


CARGO = HOME / ".cargo/bin/cargo"


def cargo_semantics(work: Path) -> dict:
    """Prove the Cargo claims of node-npm-to-cargo offline with local path dependencies."""
    import shutil
    if work.exists():
        shutil.rmtree(work)
    record = {}

    def package(path: Path, name: str, version: str, deps: str = "", main: str | None = None) -> None:
        (path / "src").mkdir(parents=True, exist_ok=True)
        (path / "Cargo.toml").write_text(
            f'[package]\nname = "{name}"\nversion = "{version}"\nedition = "2024"\n\n[dependencies]\n{deps}',
            encoding="utf-8")
        if main is None:
            (path / "src" / "lib.rs").write_text("pub fn id() -> u32 { 7 }\n", encoding="utf-8")
        else:
            (path / "src" / "main.rs").write_text(main, encoding="utf-8")

    package(work / "dep140", "dep", "1.4.0")
    package(work / "dep050", "dep", "0.5.0")
    cases = [("bare 1.3.0 accepts 1.4.0", "dep140", "1.3.0", True),
             ("=1.3.0 rejects 1.4.0", "dep140", "=1.3.0", False),
             ("bare 0.4.1 rejects 0.5.0", "dep050", "0.4.1", False)]
    for label, dep, requirement, accepted in cases:
        app = work / f"app-{len(record)}"
        package(app, "app", "0.1.0", f'dep = {{ path = "../{dep}", version = "{requirement}" }}\n',
                "fn main() { println!(\"{}\", dep::id()); }\n")
        result = run([CARGO, "build", "--offline", "-q"], cwd=app, timeout=300)
        record[label] = result.returncode == 0
        if (result.returncode == 0) != accepted:
            fail(f"node-npm-to-cargo: cargo case {label!r}: {result.stderr[-300:]}")
    lesson = load(ROOT / "lessons" / "node-npm-to-cargo.json")
    invoice = work / "invoice"
    package(invoice, "invoice", "0.1.0", "", lesson["writing"]["exampleCode"] + "\n")
    result = run([CARGO, "run", "--offline", "-q"], cwd=invoice, timeout=300)
    record["cargo run prints"] = result.stdout
    if result.stdout != "invoice 0.1.0\n":
        fail(f"node-npm-to-cargo: cargo run printed {result.stdout!r} {result.stderr[-300:]}")
    return record


def main() -> None:
    only = set(sys.argv[1:])
    expectations = load(HERE / "expectations.json")
    course = load(ROOT / "course.json")
    units = {p.stem: load(p) for p in (ROOT / "units").glob("*.json")}
    lessons = {p.stem: load(p) for p in (ROOT / "lessons").glob("*.json")}
    checks = {p.stem: load(p) for p in (ROOT / "checks").glob("*.json")}
    terms = load(ROOT / "terms.json")
    check_fields(course, units, lessons, checks, terms)
    report = {"course": COURSE_ID, "compilers": {v: run([p, "--version"]).stdout.strip() for v, p in RUSTC.items()},
              "node": run([NODE, "--version"]).stdout.strip(),
              "tsc": run([TSC, "--version"]).stdout.strip(), "lessons": {}}
    for uid in course["unitIDs"]:
        for lid in units[uid]["lessonIDs"]:
            if lid not in lessons or (only and lid not in only):
                continue
            lesson, spec, work = lessons[lid], expectations[lid], WORK / lid
            w = lesson["writing"]
            entry = {"exerciseKind": lesson["exerciseKind"], "credits": lesson["bridge"]["credits"]}
            entry["example"] = outcome(w["exampleCode"] + "\n", work / "example", {"stdout": spec["exampleStdout"]},
                                       f"{lid} example")
            entry["practice"] = outcome(w["practiceCode"] + "\n", work / "practice", spec["practice"],
                                        f"{lid} practice")
            entry["recall"] = []
            for index, (card, expect) in enumerate(zip(w["recall"], spec["recall"])):
                if card.get("code") and expect:
                    entry["recall"].append(outcome(wrap(card["code"]), work / f"recall{index}", expect,
                                                   f"{lid} recall {index + 1}"))
                elif card.get("code"):
                    fail(f"{lid}: recall {index + 1} has code but no recorded expectation")
            entry["from"] = run_from(lid, lesson, spec["from"], work / "from")
            if lid == "node-npm-to-cargo":
                entry["cargo"] = cargo_semantics(work / "cargo")
            if lesson["exerciseKind"] == "runnable":
                entry["lab"] = verify_lab(lid, checks[lid], spec["challenge"], work / "lab")
            report["lessons"][lid] = entry
            print("ok" if not any(f.startswith(lid) for f in failures) else "--", lid)
    report["failures"] = failures
    report["passed"] = not failures
    if not only:
        (HERE / "verification.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
    print(f"{len(report['lessons'])} lessons checked, {len(failures)} failures")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
