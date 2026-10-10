#!/usr/bin/env python3
"""Keep Atlas challenge answers in the explicit reveal instead of the lesson prose."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "courses/algorithms/lessons"


def main() -> None:
    changed = 0
    for path in sorted(ROOT.glob("*.challenge.json")):
        lesson = json.loads(path.read_text(encoding="utf-8"))
        original = json.dumps(lesson, ensure_ascii=False, sort_keys=True)
        answer = f"`{lesson['algorithm']['expectedAnswer']}`"
        explanation = lesson["writing"]["explanation"]
        replacements = (
            (f"the expected answer is {answer}. That output gives you a test oracle for one case, while the private checks also exercise other legal cases.",
             "predict the output before opening the answer reveal. The revealed output is a test oracle for this case, while private checks exercise other legal cases."),
            (f"If the trace cannot explain {answer}, there is a gap",
             "If the trace cannot justify your predicted output, there is a gap"),
        )
        for old, new in replacements:
            if old in explanation:
                explanation = explanation.replace(old, new, 1)
                changed += 1
        lesson["writing"]["explanation"] = explanation
        trace = lesson["depth"]["traceSteps"][1]
        old = f"why the result can still become {answer}."
        if old in trace["detail"]:
            trace["detail"] = trace["detail"].replace(
                old, "why the output follows from the maintained state.", 1)
            changed += 1
        if answer in explanation or answer in trace["detail"]:
            raise ValueError(f"Challenge answer still visible in {lesson['id']}")
        if json.dumps(lesson, ensure_ascii=False, sort_keys=True) != original:
            path.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    print(f"Removed {changed} visible answer mentions from 200 Atlas challenges")


if __name__ == "__main__":
    main()
