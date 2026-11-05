#!/usr/bin/env python3
"""Add practical paths and compiler-verified labs using the existing v1 format.

References/solutions stay in editorial/, outside delivered CoursePacks.
Re-running this script does not append duplicate lessons or change old IDs.
"""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
COURSES = ROOT / "courses"
LABS = []


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def lab(course, lesson, signature, solution, cases, task, setup="", mutant=None, preamble="", extra=""):
    """Typed, app-private calls: learners cannot replace the verification main."""
    starter = setup + signature + ' {\n    todo!("implement the contract")\n}\n'
    source = setup + signature + " {\n" + solution + "\n}\n"
    verdict = "PASS " + lesson
    required = ["pub fn " + signature.split("pub fn ", 1)[1].split("(", 1)[0].split("<", 1)[0]]
    assertions = "\n".join(f'    assert_eq!({call}, {expected}, "case {i+1}");'
                           for i, (call, expected) in enumerate(cases))
    harness = f'mod solution;\n{preamble}\nfn main() {{\n{assertions}\n{extra}\n    println!("{verdict}");\n}}\n'
    check = {"challenge": {
        "lessonID": lesson, "patternID": lesson, "projectName": lesson + "-lab",
        "source": starter, "verificationSource": harness,
        "verificationCases": [{"kind": "visible" if i == 0 else "boundary" if i == 1 else "semantic",
                               "input": call, "expectedAnswer": expected}
                              for i, (call, expected) in enumerate(cases)],
        "expectedOutput": verdict + "\n", "requiredSourceFragments": required,
        "forbiddenSourceFragments": ['todo!("implement the contract")']},
        "evidence": {"kind": "algorithmChallenge", "expectedOutput": {"kind": "exact", "value": verdict + "\n"},
                     "requiredSourceFragments": required,
                     "forbiddenSourceFragments": ['todo!("implement the contract")']}}
    path = COURSES / course / "lessons" / (lesson + ".json")
    item = read(path)
    item["exerciseKind"] = "runnable"
    item["writing"]["task"] = task + " In the Crabrix app, open the compiler lab and complete the supplied function in solution.rs. The reading question is a separate exercise."
    item["writing"]["success"] = "The local compiler accepts the changed solution and the separate verification harness finishes all normal and boundary cases. Printing a success message alone does not complete this lab."
    save(path, item)
    save(COURSES / course / "checks" / (lesson + ".json"), check)
    project = COURSES / course / "projects" / lesson
    save(project / "project.json", {"name": lesson + "-lab", "entryFile": "solution.rs"})
    (project / "solution.rs").write_text(starter)
    LABS.append({"course": course, "id": lesson, "source": source, "starter": starter,
                 "harness": harness, "expectedOutput": verdict + "\n", "mutant": mutant,
                 "signature": signature})


def existing_labs():
    lab("basics", "functions", "pub fn double(value: i32) -> i32", "    value * 2",
        [("solution::double(4)", "8"), ("solution::double(0)", "0"), ("solution::double(-7)", "-14")],
        "Return twice the input without printing it. Inputs are limited so doubling fits i32.", mutant="0")
    lab("basics", "operators", "pub fn split_count(total: u32, size: u32) -> (u32, u32)", "    (total / size, total % size)",
        [("solution::split_count(17, 5)", "(3, 2)"), ("solution::split_count(0, 3)", "(0, 0)"), ("solution::split_count(4, 7)", "(0, 4)")],
        "Return the number of full groups and the leftover count. The group size is always positive.", mutant="(0, 0)")
    lab("basics", "control-flow", "pub fn label(n: i32) -> &'static str", '    if n < 0 { "negative" } else if n == 0 { "zero" } else { "positive" }',
        [("solution::label(4)", '"positive"'), ("solution::label(0)", '"zero"'), ("solution::label(-2)", '"negative"')],
        "Return negative, zero, or positive according to the integer's sign. All branches return a string slice.", mutant='"positive"')
    lab("basics", "loops", "pub fn sum_to(n: u32) -> u32", "    let mut sum = 0;\n    for value in 1..=n { sum += value; }\n    sum",
        [("solution::sum_to(5)", "15"), ("solution::sum_to(0)", "0"), ("solution::sum_to(1)", "1"), ("solution::sum_to(100)", "5050")],
        "Sum all integers from 1 through n, inclusive, using a loop. Inputs are in 0..=100.", mutant="n")
    lab("basics", "parsing", "pub fn parse_count(text: &str) -> Result<u32, String>", '    text.trim().parse::<u32>().map_err(|_| "invalid count".to_owned())',
        [('solution::parse_count(" 12 ")', "Ok(12)"), ('solution::parse_count("")', 'Err("invalid count".to_owned())'), ('solution::parse_count("-1")', 'Err("invalid count".to_owned())'), ('solution::parse_count("4294967296")', 'Err("invalid count".to_owned())'), ('solution::parse_count("0")', 'Ok(0)')],
        "Trim and parse an unsigned 32-bit count. Return Err with the text invalid count for malformed, negative, empty, or overflowing input.", mutant="Ok(12)")
    lab("basics", "strings", "pub fn initials(text: &str) -> String", "    text.split_whitespace().filter_map(|word| word.chars().next()).collect()",
        [('solution::initials("Ada Lovelace")', '"AL"'), ('solution::initials("")', '""'), ('solution::initials("  Crab   Rust  ")', '"CR"'), ('solution::initials("Émile 🦀")', '"É🦀"')],
        "Return the first Unicode scalar of each whitespace-separated word. Preserve case and do not slice text by byte offset.", mutant='String::from("AL")')
    lab("basics", "structs", "pub fn area(rect: Rectangle) -> u32", "    rect.width * rect.height",
        [("solution::area(solution::Rectangle { width: 4, height: 3 })", "12"), ("solution::area(solution::Rectangle { width: 0, height: 9 })", "0"), ("solution::area(solution::Rectangle { width: 2, height: 8 })", "16")],
        "Use the supplied Rectangle fields to return its area. Dimensions are at most 1000.", setup="pub struct Rectangle { pub width: u32, pub height: u32 }\n\n", mutant="0")
    lab("basics", "enums", "pub fn seconds(signal: Signal) -> u32", "    match signal { Signal::Red => 30, Signal::Amber => 5, Signal::Green => 20 }",
        [("solution::seconds(solution::Signal::Red)", "30"), ("solution::seconds(solution::Signal::Amber)", "5"), ("solution::seconds(solution::Signal::Green)", "20")],
        "Match every Signal variant: Red lasts 30 seconds, Amber 5, Green 20.", setup="pub enum Signal { Red, Amber, Green }\n\n", mutant="30")
    lab("basics", "option-result", "pub fn first_number(text: Option<&str>) -> Result<Option<i32>, String>", '    text.map(|s| s.parse::<i32>().map_err(|_| "invalid".to_owned())).transpose()',
        [('solution::first_number(Some("7"))', "Ok(Some(7))"), ("solution::first_number(None)", "Ok(None)"), ('solution::first_number(Some("bad"))', 'Err("invalid".to_owned())'), ('solution::first_number(Some("-4"))', "Ok(Some(-4))")],
        "Keep missing input distinct from invalid input: None becomes Ok(None), a valid integer becomes Ok(Some(n)), and invalid text becomes Err(invalid). A match is fine; transpose is an optional extension.", mutant="Ok(None)")
    lab("basics", "collections", "pub fn counts(words: &[&str]) -> std::collections::BTreeMap<String, usize>",
        "    let mut counts = std::collections::BTreeMap::new();\n    for word in words { *counts.entry((*word).to_owned()).or_insert(0) += 1; }\n    counts",
        [('solution::counts(&["rust", "crab", "rust"])', 'std::collections::BTreeMap::from([("crab".to_owned(), 1), ("rust".to_owned(), 2)])'), ("solution::counts(&[])", "std::collections::BTreeMap::new()"), ('solution::counts(&["a", "a", "a"])', 'std::collections::BTreeMap::from([("a".to_owned(), 3)])')],
        "Count repeated words in a BTreeMap with owned keys. Keep case as supplied; empty input produces an empty map.", mutant="std::collections::BTreeMap::new()")
    lab("basics", "pattern-matching", "pub fn describe(value: Option<i32>) -> &'static str", '    match value { None => "missing", Some(0) => "zero", Some(n) if n < 0 => "negative", Some(_) => "positive" }',
        [("solution::describe(Some(3))", '"positive"'), ("solution::describe(None)", '"missing"'), ("solution::describe(Some(0))", '"zero"'), ("solution::describe(Some(-9))", '"negative"')],
        "Match None and all integer signs, using a guard for negative values.", mutant='"missing"')
    lab("basics", "ranges", "pub fn inside(n: i32, start: i32, end: i32) -> bool", "    (start..end).contains(&n)",
        [("solution::inside(2, 1, 3)", "true"), ("solution::inside(3, 1, 3)", "false"), ("solution::inside(1, 1, 3)", "true"), ("solution::inside(1, 1, 1)", "false")],
        "Check membership of the half-open range start..end, including start but excluding end. Empty ranges contain nothing.", mutant="true")
    lab("ownership", "slices", "pub fn head(values: &[i32], count: usize) -> &[i32]", "    &values[..count.min(values.len())]",
        [("solution::head(&[4, 5, 6], 2)", "&[4, 5]"), ("solution::head(&[], 3)", "&[]"), ("solution::head(&[8], 9)", "&[8]"), ("solution::head(&[8], 0)", "&[]")],
        "Borrow at most count elements from the start, clamping to length. Return a subslice without allocating or panicking.", mutant="&values[..0]")
    lab("ownership", "copy-clone", "pub fn duplicate(value: &str) -> (String, String)", "    let first = value.to_owned();\n    let second = first.clone();\n    (first, second)",
        [('solution::duplicate("crab")', '("crab".to_owned(), "crab".to_owned())'), ('solution::duplicate("")', '(String::new(), String::new())'), ('solution::duplicate("🦀")', '("🦀".to_owned(), "🦀".to_owned())')],
        "Return two independent owned strings containing the borrowed input. The caller keeps its original text.", mutant="(String::new(), String::new())")
    lab("ownership", "closures", "pub fn keep_above(values: &[i32], minimum: i32) -> Vec<i32>", "    values.iter().copied().filter(|n| *n > minimum).collect()",
        [("solution::keep_above(&[2, 5, 1, 5], 2)", "vec![5, 5]"), ("solution::keep_above(&[], 0)", "vec![]"), ("solution::keep_above(&[-2, 0, 1], 0)", "vec![1]")],
        "Use a closure that captures minimum to keep strictly greater values in original order, including duplicates.", mutant="vec![]")
    lab("ownership", "iterators", "pub fn even_sum(values: &[i32]) -> i32", "    values.iter().copied().filter(|n| n % 2 == 0).sum()",
        [("solution::even_sum(&[1, 2, 3, 4])", "6"), ("solution::even_sum(&[])", "0"), ("solution::even_sum(&[-4, -1, 2])", "-2"), ("solution::even_sum(&[3, 5])", "0")],
        "Sum only even integers with iterator adapters. Inputs and their sum fit i32.", mutant="0")
    lab("ownership", "generics", "pub fn larger<T: Ord>(left: T, right: T) -> T", "    if left >= right { left } else { right }",
        [("solution::larger(3, 8)", "8"), ("solution::larger(-2, -9)", "-2"), ('solution::larger("a".to_owned(), "z".to_owned())', '"z"'), ("solution::larger(4, 4)", "4")],
        "Return the larger owned input for any Ord type, without adding Copy or Clone bounds. This lab also calls the function with String.", mutant="left")
    lab("ownership", "traits", "pub fn render(value: &impl std::fmt::Display) -> String", '    format!("value={value}")',
        [("solution::render(&42)", '"value=42"'), ('solution::render(&"crab")', '"value=crab"'), ("solution::render(&false)", '"value=false"')],
        "Accept a borrowed Display value and format value= followed by its display representation.", mutant="String::new()")


def lesson(course, unit, id, title, concept, summary, rule, paragraphs, code, task,
           question, answers, correct, feedback, misconception, correction, steps,
           transfer, minutes=16):
    path = COURSES / course / "units" / (unit + ".json")
    u = read(path)
    if id not in u["lessonIDs"]:
        u["lessonIDs"].append(id)
    save(path, u)
    item = {"id": id, "parentID": unit, "order": u["lessonIDs"].index(id),
            "title": title, "concept": concept, "minutes": minutes,
            "exerciseKind": "planned", "writing": {
                "summary": summary, "rule": rule, "explanation": "\n\n".join(paragraphs),
                "exampleCode": code, "exampleCaption": concept,
                "practiceCode": code, "task": task, "success": feedback,
                "question": question, "answers": answers, "correctAnswer": correct,
                "feedback": feedback}, "depth": {
                "misconception": misconception, "correction": correction,
                "traceSteps": [{"title": t, "detail": d} for t,d in steps],
                "transferChallenge": transfer, "connections": []}}
    # Regeneration preserves illustrations produced by the established diagram tool.
    lp = COURSES / course / "lessons" / (id + ".json")
    if lp.exists() and read(lp).get("illustration"):
        item["illustration"] = read(lp)["illustration"]
    save(lp, item)
    save(COURSES / course / "checks" / (id + ".json"), {"evidence": {"kind": "reasoning", "correctAnswer": correct}})


def unit(course, id, title, subtitle):
    path = COURSES / course / "course.json"
    c = read(path)
    if id not in c["unitIDs"]:
        c["unitIDs"].append(id)
    save(path, c)
    up = COURSES / course / "units" / (id + ".json")
    save(up, {"id": id, "parentID": course, "order": c["unitIDs"].index(id),
              "level": c["unitIDs"].index(id) + 1, "title": title, "subtitle": subtitle,
              "lessonIDs": read(up)["lessonIDs"] if up.exists() else []})


def main():
    existing_labs()
    # The route modules contain the teaching text and typed verification contracts.
    from routes import add_routes
    add_routes(unit, lesson, lab)
    runtime = COURSES / "concurrency/lessons/async-runtime.json"
    item = read(runtime)
    item["writing"]["exampleCode"] = '''// [dependencies.tokio]
// version = "1"
// default-features = false
// features = ["rt"]
// No runtime attribute macro is needed.
fn main() {
    use tokio::runtime::Builder;
    let runtime = Builder::new_current_thread()
        .build().unwrap();
    let value = runtime.block_on(compute());
    println!("{value}");
}
async fn compute() -> u32 { 42 }'''
    item["writing"]["exampleCaption"] = "A synchronous main explicitly asks a current-thread executor to poll the future."
    # Replace the earlier attribute-specific statement as well as the example.
    explanation = item["writing"]["explanation"]
    explanation = explanation.replace("#[tokio::main]", "the runtime entry adapter")
    if "Execution profile:" not in explanation:
        explanation += "\n\nExecution profile: this is a Cargo example with Tokio's rt feature, not a standard-library-only program. The explicit current-thread builder avoids procedural macros and the much broader full feature set. On desktop Cargo it prints 42. In Crabrix, consult the prepared package compatibility report before running it; native sockets, threads, timers, and every other Tokio feature are not implied by this example."
    item["writing"]["explanation"] = explanation
    save(runtime, item)
    dependencies = COURSES / "projects/lessons/dependencies.json"
    item = read(dependencies)
    if "Execution profile:" not in item["writing"]["explanation"]:
        item["writing"]["explanation"] += "\n\nExecution profile: the manifest shown here is a desktop Cargo dependency example. Serde's derive feature requires procedural-macro support, not just a downloaded runtime library. In Crabrix, inspect the exact package, feature, build-script, and macro compatibility report first. The Files & Data unit separates a dependency-free parsing lab from a labelled Serde Cargo example."
    save(dependencies, item)
    # Add useful next/previous connections only to the appended routes.
    for cid, uid in [("projects", "files-data"), ("projects", "reliability-labs"),
                     ("ownership", "api-boundaries"), ("concurrency", "async-operations"), ("systems", "wasm-wasi")]:
        ids = read(COURSES / cid / "units" / (uid + ".json"))["lessonIDs"]
        for i, lid in enumerate(ids):
            p = COURSES / cid / "lessons" / (lid + ".json"); item = read(p)
            item["depth"]["connections"] = []
            for direction, neighbor in [("previous", i - 1), ("next", i + 1)]:
                if 0 <= neighbor < len(ids):
                    other = read(COURSES / cid / "lessons" / (ids[neighbor] + ".json"))
                    item["depth"]["connections"].append({"direction": direction, "title": other["title"], "concept": other["concept"]})
            save(p, item)
    versions = {"basics": "1.0.8", "ownership": "1.0.8", "projects": "1.0.8",
                "concurrency": "1.0.7", "systems": "1.0.8"}
    for cid, version in versions.items():
        p = COURSES / cid / "course.json"; c = read(p)
        c["contentVersion"] = version; save(p, c)
    for cid in versions:
        for p in (COURSES / cid / "lessons").glob("*.json"):
            item = read(p)
            if item["parentID"] not in {"files-data", "reliability-labs", "api-boundaries", "async-operations", "wasm-wasi"} and item["id"] != "async-runtime":
                continue
            with tempfile.TemporaryDirectory() as temp:
                source = Path(temp) / "main.rs"
                source.write_text(item["writing"]["exampleCode"])
                subprocess.run(["rustfmt", "--edition", "2024", "--config", "max_width=52,use_small_heuristics=Off", str(source)], check=True, capture_output=True)
                item["writing"]["exampleCode"] = source.read_text()
            if item["id"] != "async-runtime":
                item["writing"]["practiceCode"] = item["writing"]["exampleCode"]
            save(p, item)
    save(BASE / "lab-references.json", LABS)
    print(f"Authored {len(LABS)} verified lab contracts")


if __name__ == "__main__":
    main()
