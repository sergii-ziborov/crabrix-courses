#!/usr/bin/env python3
"""Add worked reasoning and category-specific guidance to Atlas lessons once.

The authored pattern metadata supplies the task, sample, expected answer, core
idea, complexity, and Rust sketch. This script turns those anchors into distinct
model, recognition, and challenge readings without changing checks or sources.
"""

import json
from pathlib import Path


COURSES = Path(__file__).resolve().parents[1] / "courses" / "algorithms"

# The same topic needs different advice when learners model it, select it, and
# implement it. Each entry is deliberately broad enough for its ten patterns.
CATEGORY = {
    "scans": (
        "A scan turns a sequence into a small piece of state. Say what the state means after the first i elements, before you describe a loop body.",
        "Ask whether one pass is enough, whether order matters, and whether a later query will need information you already discarded.",
        "Use an empty slice and a one-element slice as checks. Initial values must not silently assume that at least one item exists.",
        "A borrowed slice and a for loop usually express the traversal clearly; distinguish an index you need to return from a value you merely read.",
    ),
    "hashing": (
        "A key-derived representation lets later work reuse an earlier fact. It may be a set, a map from keys to state, compressed ranks, or a rolling fingerprint; name which one this pattern uses.",
        "Look for repeated membership, grouping, or a reusable key representation. A sorted structure may be preferable when deterministic order is part of the requirement.",
        "Check missing keys, repeated keys, and collisions conceptually; expected constant-time operations are not a worst-case promise.",
        "In Rust, use HashSet for presence and HashMap for associated state. Compression and rolling hashes need their own arrays or arithmetic; do not force every hashing pattern into a map.",
    ),
    "ranges": (
        "A range method summarizes intervals so the same information is not recomputed. A static prefix table and an updateable tree make different tradeoffs; define endpoint conventions first.",
        "Precomputation pays when many ranges are queried. If values change between queries, an updateable structure may be needed; for one small query, a direct walk is simpler.",
        "Test the first and last position, an empty range where permitted, and the boundary immediately after an update.",
        "Allocate an extra prefix slot when a zero-length prefix simplifies indexing, and use a numeric type large enough for accumulated values.",
    ),
    "two-pointers": (
        "Two positions move according to a monotone fact: after one comparison, some candidates can be ruled out permanently. Name that fact.",
        "Check whether the input is sorted, whether you may reorder it, and whether moving a pointer preserves the answer you seek.",
        "Test pointers meeting, crossing, duplicate values, and the smallest valid input; many off-by-one errors hide there.",
        "Use explicit bounds for both indices. If the algorithm mutates a vector, separate read and write positions so ownership stays clear.",
    ),
    "sliding-window": (
        "A window is a contiguous interval with a maintained summary. Describe what entering the right edge adds and what leaving the left edge removes.",
        "Choose this family when a valid window can be repaired by moving one boundary; non-monotone constraints may need a different method.",
        "Test an empty window, a window spanning the whole input, and a case where the left edge must advance several times.",
        "Represent bounds as a half-open range when possible. Keep counts and the window length in sync when shrinking it.",
    ),
    "stacks-queues": (
        "A stack remembers unfinished work in last-in-first-out order; a queue processes work in first-in-first-out order. Say what each stored item still needs.",
        "Look for nested structure, next-greater relationships, or ordered processing. A plain scan is enough when no unresolved state must be retained.",
        "Check empty containers, one item, repeated equal values, and the work left in the structure after the input ends.",
        "Vec works as a stack; VecDeque supplies efficient operations at both ends. Avoid removing from the front of a Vec in a long loop.",
    ),
    "sorting-selection": (
        "Sorting establishes global order; selection asks only for a rank or partition. Explain which comparisons make progress toward that goal.",
        "Before sorting everything, ask whether a single statistic is enough and whether stable order among equal keys matters.",
        "Test all-equal keys, already ordered input, reverse order, and extreme pivot or bucket distributions.",
        "Rust slice sorting is available, but an exercise asking for the algorithm requires the actual invariant and mutation steps, not a library shortcut.",
    ),
    "binary-search": (
        "Binary search maintains an interval that is still capable of containing the answer. State precisely why the discarded half cannot contain it.",
        "It needs ordering, a monotone predicate, or another proved structure that lets one half be discarded; merely containing numbers is not enough.",
        "Check no match, duplicate matches, the first and last valid positions, and an answer at the boundary of the search domain.",
        "Use half-open bounds consistently and compute the midpoint without overflowing large integer indices.",
    ),
    "linked-lists": (
        "A list algorithm changes relationships between nodes, not just values. Draw the next pointers before and after each mutation.",
        "Look for tasks where node identity or one-way traversal matters. An indexed vector solution can hide the pointer constraint rather than solve it.",
        "Check an empty list, one node, a head or tail change, and cycles when the problem allows them.",
        "Rust ownership makes linked structures explicit: use the provided node type, take links carefully, and preserve access to the remaining chain.",
    ),
    "trees": (
        "A tree result is built from a node and its children. Decide whether information flows downward, upward, or in level order.",
        "Look for hierarchy and parent-child structure; a plain sequence algorithm loses the branching relationships.",
        "Test a missing root, a leaf, a skewed tree, and equal or duplicate values when ordering rules depend on them.",
        "Use references for read-only traversals and make the stack or queue explicit when recursion depth might be large.",
    ),
    "heaps-streaming": (
        "A heap keeps the current extremum accessible while new items arrive. Explain what belongs in the heap and what may be discarded.",
        "Use it when only top-ranked candidates or repeated next-best extraction matters; sorting the entire stream may waste work.",
        "Check an empty stream, k equal to zero or to the input length, duplicate priorities, and stale entries if deletion is lazy.",
        "Rust BinaryHeap is a max-heap; Reverse can express a min-heap. Keep the heap's ordering key separate from unrelated payload data.",
    ),
    "graph-traversal": (
        "A graph method needs an explicit vertex-and-edge representation. For traversal, define when a vertex becomes seen: on insertion into the frontier or on removal.",
        "Choose a representation for the operations first; when traversing, DFS explores depth and BFS follows equal-cost layers. Directed edges and disconnected components change the plan.",
        "Test an isolated vertex, a cycle, duplicate edges, and a graph whose starting vertex reaches only one component.",
        "An adjacency list and VecDeque make breadth-first work explicit. Mark before enqueuing to avoid duplicate frontier entries.",
    ),
    "weighted-graphs": (
        "Edge weights change what a path means. State whether the objective is minimum distance, a spanning structure, or feasible flow before choosing state.",
        "Inspect weight signs and graph direction: non-negative shortest paths, negative edges, and zero-one weights support different algorithms.",
        "Check disconnected vertices, parallel edges, zero weights, and whether an unreachable result has a defined representation.",
        "Use numeric types wide enough for distances, weights, or capacities. In shortest-path heap variants, skip stale queue entries and guard sentinel arithmetic.",
    ),
    "backtracking": (
        "Most patterns here explore a decision tree; meet-in-the-middle instead enumerates two halves and combines them. Define the partial choice or subset summary that the pattern retains.",
        "Use pruning when partial choices can already be ruled out. Meet-in-the-middle instead trades two exhaustive half-enumerations for a smaller search space.",
        "Test no solution, one solution, duplicate inputs, and the order in which candidates are tried if output order is observable.",
        "For recursive search, push a choice, recurse, then undo it; for meet-in-the-middle, collect each half before matching them. In Rust, clone a path only when storing a completed answer.",
    ),
    "greedy-intervals": (
        "A greedy step commits to a local choice. Give the exchange or dominance reason that an optimal solution can still include that choice.",
        "When the method sorts intervals or events, use the coordinate and tie break required by its proof. Other greedy walks keep an invariant without sorting.",
        "Test touching intervals, equal endpoints, empty input, and a locally attractive choice that blocks a better future choice.",
        "Keep interval endpoint conventions explicit where they apply. If sorting is part of the method, its Rust comparator must encode the proof's exact tie break.",
    ),
    "dynamic-1d": (
        "A one-dimensional DP state summarizes a prefix or a single parameter. Define its meaning before writing a recurrence.",
        "Choose a recurrence when subproblems overlap. Some patterns summarize a frontier instead of a full DP table; either representation needs an invariant, and any greedy shortcut needs proof.",
        "Test the base state, the first transition, impossible states, and whether an in-place update accidentally reuses an item twice.",
        "Use Option or a safe sentinel for unreachable states, and choose an iteration direction that matches the recurrence's dependencies.",
    ),
    "dynamic-2d": (
        "A multidimensional or structured DP state records the information needed to identify a subproblem: two prefixes, an interval, a bitmask, a tree node, or a resource limit.",
        "Write the dependency arrows before choosing loop order; a recurrence that reads the future cannot be filled left to right without adjustment.",
        "Test base states, boundary cells or subsets, ties, and whether a compressed representation overwrites a value still needed later.",
        "Index tables consistently where the state is tabular. Compress dimensions only after the full recurrence and its dependency order are clear.",
    ),
    "strings-tries": (
        "String algorithms compare symbols or prefixes, but a Rust String is UTF-8 bytes. State whether the task means bytes, scalar values, or grapheme clusters.",
        "Look for repeated prefix queries or pattern matching before choosing a trie or preprocessing; a one-off short search may not need either.",
        "Test empty pattern and text, repeated characters, overlapping matches, and non-ASCII input if the contract allows it.",
        "Use bytes only when the input contract permits byte-wise matching. Never index a String as though every character occupied one byte.",
    ),
    "math-bits": (
        "An arithmetic or bitwise transformation relies on an identity. Write that identity and the domain in which it holds.",
        "Check number size, sign, and modulus assumptions before using a shortcut; not every inverse or division exists.",
        "Test zero, one, powers of two, maximum input size, and overflow or underflow around intermediate products.",
        "Use explicit integer widths and checked arithmetic when input bounds require them. Distinguish bit positions from numeric values.",
    ),
    "advanced-structures": (
        "An advanced structure or offline query order packages an invariant across operations. Name what each node, block, or reordered query state stores.",
        "Choose it when the required operation sequence, query volume, or substring structure exceeds a simple scan or prefix summary; compare the real time and memory limits first.",
        "Test empty ranges, repeated updates, undo operations where supported, and the exact boundary between adjacent blocks.",
        "Keep representation and operations separate in Rust. Verify a tiny instance against a straightforward reference implementation before optimizing.",
    ),
}


def natural(text: str) -> str:
    text = text.strip()
    return text[:1].lower() + text[1:] if text else text


def extend(lesson: dict) -> None:
    algorithm = lesson["algorithm"]
    model, selection, boundary, rust = CATEGORY[algorithm["categoryID"]]
    title = lesson["title"].removeprefix("Challenge: ").split(":")[0]
    idea = algorithm["idea"].rstrip(".") + "."
    task = algorithm["task"].rstrip(".") + "."
    sample = algorithm["visibleInput"]
    answer = algorithm["expectedAnswer"]
    complexity = algorithm["complexity"]
    sketch = algorithm["rustSketch"].strip()
    sketch_kind = ("The supplied Rust sketch is an invariant note rather than a complete program. Turn it into explicit state and transitions before coding."
                   if sketch.startswith("//") else
                   "The supplied Rust sketch is a starting point. Identify what it stores, how one iteration changes it, and whether it already solves the exact task or only demonstrates a related operation.")
    stage = algorithm["stage"]
    if stage == "model":
        paragraphs = [
            f"Begin with the concrete question: {task} For the visible input `{sample}`, the stated result is `{answer}`. Before reading code, name the smallest piece of information that must survive from one step to the next. {model} That is the mental model for {title}; it gives you a reason for each update instead of a line of code to memorise.",
            f"The core mechanism is this: {idea} Treat it as a claim to test after every operation. Write down the state before the first operation, update it once, and ask which part of the claim is still true. If an item is skipped, inserted, or removed, explain why that action cannot destroy an answer that should be retained. A useful trace has columns for the current input position, the state before the step, the action, and the state afterward. Use the visible sample until the expected result becomes inevitable rather than merely plausible.",
            f"Now inspect the Rust sketch, not just its final expression. {sketch_kind} {rust} Translate the variable names into roles: input, carried state, temporary candidate, and output. Borrow data that only needs reading; copy or move data only when the algorithm actually needs ownership. If the sketch leaves out parsing or edge handling, list those missing steps before calling it a complete solution.",
            f"Finally justify the stated bound, {complexity}. Count how often an item, edge, state, or candidate can enter the main operation; do not infer the bound from the number of loop keywords alone. {boundary} Predict the result for a smallest legal input and for one case that stresses the invariant. If your prediction disagrees with a hand trace, repair the state definition before changing code.",
        ]
    elif stage == "recognize":
        paragraphs = [
            f"A problem is a good match for {title} when it asks for {natural(algorithm['useCases'])}. Here the concrete task is: {task} The visible input `{sample}` is an example, not a definition of the whole problem. Ask what operations the solution must support and what the input guarantees. {selection} The right choice follows from those guarantees, not from a familiar noun in the prompt.",
            f"The decisive invariant is: {idea} Try to say why it applies to the task without quoting the implementation. Which fact becomes known after one update, and which possible answers remain? {model} If that claim cannot be maintained on a legal input, the pattern is wrong or one of its preconditions is missing. A counterexample is more useful than a vague warning: change one property of the sample, trace the first two steps, and identify the exact claim that fails.",
            f"Compare costs before committing. The advertised bound is {complexity}; identify the operation responsible for it and the extra memory it needs. Then compare a straightforward alternative: a direct scan, full sort, or repeated recomputation may be easier but can pay for the same work many times. Do not choose the more elaborate method just because it has a famous name. For the sample, predict `{answer}` and explain which part of the state lets the method reach that result.",
            f"When the prompt is ambiguous, ask about input size, ordering, duplicates, and required output format. {boundary} {rust} The Rust sketch can show a useful primitive without proving that the whole task is solved; connect each primitive to the requested output. You should be able to name a fitting case, a near miss, and the assumption separating them before writing the first line.",
        ]
    else:
        paragraphs = [
            f"Solve the exact task, not just the visible example: {task} On input `{sample}`, the expected answer is `{answer}`. That output gives you a test oracle for one case, while the private checks also exercise other legal cases. Start by stating the input grammar and output format in your own words. Parse the complete input, including surrounding whitespace, before relying on any convenient positions in the example.",
            f"Build the solution around one maintained claim: {idea} Decide what state represents that claim, how it is initialized, what a single update does, and when the algorithm stops. {model} Trace the visible input by hand and record at least two intermediate states, not only the final answer. If the trace cannot explain `{answer}`, there is a gap between the idea and the implementation.",
            f"Use the Rust sketch as a guide, not a substitute for a complete `solve` function. {sketch_kind} {rust} Keep parsing separate from the algorithm so a bad input assumption does not look like a logic bug. Make the return value reflect the computed state; printing or returning the visible expected answer directly only passes one example. Where the state owns data, be deliberate about borrowing and mutation instead of cloning to silence a compiler error.",
            f"Check both correctness and cost. The intended bound is {complexity}; explain which operation dominates it and how many times the input can trigger that operation. {boundary} Add one small case that should succeed, one boundary case, and one case chosen to challenge the invariant. Compare your hand result with the program's result, then use a failing case to fix the earliest incorrect state transition rather than patching the final output.",
        ]
    lesson["writing"]["explanation"] = "\n\n".join(paragraphs)
    lesson["depth"]["traceSteps"] = [
        {"title": "Define the state", "detail": f"For `{sample}`, write the state before the first update. Explain how it represents this claim: {idea} {model}"},
        {"title": "Trace a transition", "detail": f"Apply one legal update to the sample. Record what changes, what stays true, and why the result can still become `{answer}`. {rust}"},
        {"title": "Probe the boundary", "detail": f"Check a smallest input and a case that challenges the assumption. {boundary} Defend the {complexity} bound by counting actual work."},
    ]
    lesson["depth"]["transferChallenge"] = (
        f"Change the visible input `{sample}` in one meaningful way: remove an item, repeat a key, alter an edge, or move a boundary as the task permits. "
        f"Predict the new output before running code. State which part of the invariant from {title} survives, which state must be updated, "
        f"and whether the {complexity} bound still holds. {selection}"
    )
    lesson["minutes"] = max(lesson["minutes"], 12 if stage != "challenge" else 15)


def main() -> None:
    count = 0
    for path in sorted((COURSES / "lessons").glob("*.json")):
        lesson = json.loads(path.read_text(encoding="utf-8"))
        if lesson["algorithm"]["categoryID"] not in CATEGORY:
            raise ValueError(f"missing category guidance for {lesson['id']}")
        if "\n\n" in lesson["writing"]["explanation"]:
            raise ValueError(f"already expanded: {lesson['id']}")
        extend(lesson)
        path.write_text(json.dumps(lesson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        count += 1
    print(f"Expanded {count} Algorithm Atlas lessons")


if __name__ == "__main__":
    main()
