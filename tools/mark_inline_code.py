#!/usr/bin/env python3
"""Mark unambiguous Rust syntax in lesson prose for app and web renderers.

Only prose fields are changed. Existing Markdown code spans and source samples
are left intact. Run this before recomputing CoursePack digests.
"""

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "courses"
TYPE = ("Vec", "VecDeque", "String", "Option", "Result", "Some", "None", "Ok", "Err",
        "HashMap", "HashSet", "BinaryHeap", "Box", "Arc", "Rc", "Cell", "RefCell",
        "Mutex", "RwLock", "Pin", "Future", "Iterator", "Display", "Debug", "Send",
        "Sync", "FnOnce", "FnMut", "usize", "isize", "i8", "i16", "i32", "i64",
        "u8", "u16", "u32", "u64", "bool", "char")
TYPE_PATTERN = "|".join(map(re.escape, TYPE))
PATTERN = re.compile(
    r"(?<![\w`])(?:"
    r"let\s+(?:mut\s+)?[A-Za-z_]\w*\s*=\s*[^;`\n]{1,75};"
    r"|#\[[^\]`\n]{1,70}\]"
    r"|&(?:mut\s+)?(?:str|[A-Z][A-Za-z_]\w*)"
    r"|[A-Za-z_]\w*(?:::[A-Za-z_]\w*)+"
    r"|[A-Za-z_]\w*\[\d+\]"
    r"|(?:[A-Za-z_]\w*(?:\(\))?)(?:\.[A-Za-z_]\w*\(\)){1,3}"
    r"|(?:println|eprintln|format|dbg|vec|assert|assert_eq)!"
    r"|\b(?:len|chars|bytes|clone|unwrap|expect|collect|iter|iter_mut|as_ref|as_mut|parse|count)\(\)"
    r"|\bcargo\s+(?:test|run|check|build|doc|fmt|clippy)(?:\s+--[a-z-]+)*"
    r"|\b(?:Cargo\.toml|main\.rs|lib\.rs)\b"
    rf"|\b(?:{TYPE_PATTERN})\b"
    r"|\b(?:let|mut|fn|impl|unsafe|async|await)\b"
    r")"
)


def mark(text: str) -> str:
    if text.count("`") % 2:
        raise ValueError(f"unbalanced Markdown code spans: {text[:80]}")
    parts = text.split("`")
    for index in range(0, len(parts), 2):
        parts[index] = PATTERN.sub(lambda match: f"`{match.group(0)}`", parts[index])
    return "`".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report pending fields without editing")
    args = parser.parse_args()
    changed_lessons = 0
    changed_fields = 0
    for path in sorted(ROOT.glob("*/lessons/*.json")):
        lesson = json.loads(path.read_text(encoding="utf-8"))
        before = json.dumps(lesson, ensure_ascii=False, sort_keys=True)
        writing = lesson.get("writing", {})
        for field in ("summary", "explanation", "rule", "task", "success", "feedback",
                      "question", "exampleCaption"):
            if field in writing:
                replacement = mark(writing[field])
                if replacement != writing[field]:
                    writing[field] = replacement
                    changed_fields += 1
        depth = lesson.get("depth", {})
        for field in ("misconception", "correction", "transferChallenge"):
            if field in depth:
                replacement = mark(depth[field])
                if replacement != depth[field]:
                    depth[field] = replacement
                    changed_fields += 1
        for step in depth.get("traceSteps", []):
            replacement = mark(step["detail"])
            if replacement != step["detail"]:
                step["detail"] = replacement
                changed_fields += 1
        if json.dumps(lesson, ensure_ascii=False, sort_keys=True) != before:
            changed_lessons += 1
            if not args.check:
                path.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")
    print(f"{'Pending' if args.check else 'Marked'}: {changed_fields} prose fields in {changed_lessons} lessons")


if __name__ == "__main__":
    main()
