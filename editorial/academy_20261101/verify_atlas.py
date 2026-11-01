#!/usr/bin/env python3
"""Verify the Atlas against its expected answers, for real, with rustc --edition 2024.

1. Every worked program in the lessons compiles alone, stays rustfmt-clean and prints
   its stated answer.
2. Every case input, plus seeded random inputs for the programs and contracts this pass
   changed, runs through the typed Rust reference and the independent Python oracle.
3. Every packaged harness runs on its extended cases behind a typed adapter, as in
   academy_20261027/verify_harnesses.py, and rejects corrupt results.
4. Static checks cover quizzes, rule and challenge leaks, starters and editorial text.

Adapters dispatch known inputs to typed functions. They are test infrastructure and do
not claim to test a learner's text parser. Finite fixtures are evidence for these inputs,
not a proof for all inputs or of any asymptotic bound.
"""
from concurrent.futures import ThreadPoolExecutor
import json
import random
import re
import subprocess
import sys

from atlas_overlay import BASE, CODE, CSV, HELPERS, PROGRAMS, REPO, SEMI, call, r, solve
from adversarial import CASES as ADDED
from apply_pass import BASELINE, harness, checker_of, PARTITION_CHECKER

WORK = REPO / 'build/academy-20261101/verify'
COURSE = REPO / 'courses/algorithms'
ANSWER = re.compile(r'For teaching input `(.*?)`, the worked program returns (`[^`]*`|An empty output string)', re.S)
LEAK = re.compile(r'previous(ly)? published|published answer|belongs to a different|now explicit', re.I)
BAD_SPANS = ('`String` algorithms', '`Some` patterns', '`String` Two Pointers', '`not a valid result`')


def lesson(pattern, stage):
    return json.loads((COURSE / 'lessons' / f'algorithm.{pattern}.{stage}.json').read_text())


def strings(value, skip=('exampleCode', 'practiceCode', 'rustSketch', 'contentDigest', 'illustration')):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item, skip)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key not in skip:
                yield from strings(item, skip)


def fuzz_inputs(rng):
    """Seeded legal inputs, for differential runs of changed programs and contracts."""
    def ints(low, high, count):
        return [rng.randint(low, high) for _ in range(count)]

    def compact_tree():
        queue, tokens, next_value = 1, [str(rng.randint(1, 9))], 2
        while queue and len(tokens) < 12:
            queue -= 1
            for _ in range(2):
                if rng.random() < 0.6:
                    tokens.append(str(next_value))
                    next_value += 1
                    queue += 1
                else:
                    tokens.append('null')
        while tokens[-1] == 'null':
            tokens.pop()
        return '[' + ','.join(tokens) + ']'

    def bst():
        keys = rng.sample(range(1, 15), rng.randint(1, 7))
        nodes = {}
        root = keys[0]
        for key in keys[1:]:
            at = root
            while True:
                side = 0 if key < at else 1
                child = nodes.setdefault(at, [None, None])[side]
                if child is None:
                    nodes[at][side] = key
                    break
                at = child
        tokens, queue = [], [root]
        while queue:
            at = queue.pop(0)
            tokens.append('null' if at is None else str(at))
            if at is not None:
                queue.extend(nodes.get(at, [None, None]))
        while tokens[-1] == 'null':
            tokens.pop()
        return '[' + ','.join(tokens) + ']'

    out = {}
    for _ in range(40):
        n = rng.randint(2, 8)
        out.setdefault('remove-nth-from-end', []).append('->'.join(map(str, ints(0, 9, n))))
        order = list(range(1, n))
        rng.shuffle(order)
        order = [0] + order
        links = [None] * n
        for a, b in zip(order, order[1:]):
            links[a] = b
        values = ints(1, 4, n)
        random_links = [rng.choice([None] + list(range(n))) for _ in range(n)]
        show = lambda items, empty: '[' + ','.join(empty if x is None else str(x) for x in items) + ']'
        out.setdefault('copy-random-list', []).append(f'values={show(values, "")} next={show(links, "none")} random={show(random_links, "null")}')
        out.setdefault('rolling-fingerprint', []).append(f'digits={show(ints(0, 9, rng.randint(1, 9)), "")}')
        window = show(ints(-9, 9, rng.randint(3, 9)), '')
        out.setdefault('rolling-window-statistic', []).extend([window, 'variance=' + window])
        out.setdefault('tree-serialize', []).append('tree=' + compact_tree())
        word = ''.join(rng.choice('abc') for _ in range(rng.randint(1, 6)))
        other = list(word)
        if rng.random() < 0.5:
            rng.shuffle(other)
        else:
            other[0] = rng.choice('abc')
        out.setdefault('hash-frequency', []).append(f'{word}; {"".join(other)}')
        walls = sorted({(rng.randint(0, 3), rng.randint(0, 3)) for _ in range(rng.randint(0, 6))} - {(0, 0), (3, 3)})
        out.setdefault('a-star', []).append('start=0,0 goal=3,3' + (' walls=' + ','.join(f'({a},{b})' for a, b in walls) if walls else ''))
        words = sorted({''.join(rng.choice('ab') for _ in range(3)) for _ in range(rng.randint(1, 6))})
        out.setdefault('bidirectional-bfs', []).append(f'aaa -> bbb via [{",".join(words)}]')
        live, tokens = [], []
        for _ in range(rng.randint(1, 8)):
            if live and rng.random() < 0.4:
                value = rng.choice(live)
                live.remove(value)
                tokens.append(f'delete{value}')
            else:
                value = rng.randint(1, 5)
                live.append(value)
                tokens.append(f'push{value}')
        out.setdefault('lazy-heap-deletion', []).append(' '.join(tokens) + ' min')
        out.setdefault('min-max-tracking', []).append(show([rng.choice([-2**31, 2**31 - 1, rng.randint(-9, 9)]) for _ in range(n)], ''))
        cycle_links = [rng.choice([None] + list(range(n))) for _ in range(n)]
        out.setdefault('list-cycle', []).append(f'values={show(ints(1, 2, n), "")} next={show(cycle_links, "none")}')
        pairs = ','.join(f'({rng.randint(0, 3)},{chr(97 + i)})' for i in range(n))
        out.setdefault('insertion-sort', []).append(f'[{pairs}]')
        out.setdefault('bst-search-insert', []).append(f'BST={bst()} order=preorder')
        out.setdefault('predicate-partition', []).append(f'arranged={show(ints(0, 9, n), "")}')
        gas, cost = ints(0, 4, n), ints(0, 4, n)
        out.setdefault('gas-station', []).append(f'gas={show(gas, "")} cost={show(cost, "")}')
        out.setdefault('lower-bound', []).append(show(sorted(ints(0, 8, n)), ''))
        out.setdefault('upper-bound', []).append(show(sorted(ints(0, 8, n)), ''))
        out.setdefault('combination-sum', []).append('candidates=' + show(sorted(set(ints(1, 8, rng.randint(1, 4)))), ''))
        out.setdefault('kth-stream', []).append(show(ints(0, 9, rng.randint(3, 8)), ''))
        out.setdefault('selection-sort', []).append(show(ints(0, 4, n), ''))
    out['permutations'] = ['list=' + show(rng.sample(range(1, 9), k), '') for k in (1, 2, 3, 4, 5)]
    return {pattern: list(dict.fromkeys(inputs)) for pattern, inputs in out.items()}


def formatting(expressions):
    if any('semicolon(' in x for x in expressions):
        return CSV + SEMI
    return CSV if any('csv(' in x for x in expressions) else ''


def helpers_of(code):
    return ''.join(h for word, h in HELPERS.items() if re.search(r'\b' + word + r'\b', code))


def compile_and_run(name, source, argv=()):
    path = WORK / f'{name}.rs'
    path.write_text(source)
    compiled = subprocess.run(['rustc', '--edition=2024', '--test', '-A', 'warnings', str(path), '-o', str(WORK / name)], capture_output=True, text=True)
    (WORK / f'{name}.compile.log').write_text(compiled.stdout + compiled.stderr)
    if compiled.returncode:
        print(compiled.stderr[:12000])
        raise SystemExit(1)
    tested = subprocess.run([str(WORK / name), '--test-threads=4', *argv], capture_output=True, text=True, timeout=600)
    (WORK / f'{name}.log').write_text(tested.stdout + tested.stderr)
    tail = re.search(r'test result: .*', tested.stdout)
    return tested.returncode == 0, tail[0] if tail else tested.stdout[-800:] + tested.stderr[-800:]


def fixtures_suite(cases, fuzz):
    suites, count = [], 0
    for pattern, code in CODE.items():
        inputs = list(dict.fromkeys(cases[pattern] + fuzz.get(pattern, [])))
        expressions = [call(pattern, text) for text in inputs]
        tests = []
        for i, (text, expression) in enumerate(zip(inputs, expressions)):
            tests.append(f'#[test] fn case_{i}() {{ assert_eq!({expression},{r(solve(pattern, text))},"{{}}",{r(pattern + " " + text)}); }}')
        count += len(tests)
        suites.append('#[allow(dead_code)] mod ' + pattern.replace('-', '_') + ' {\n' + helpers_of(code) + formatting(expressions) + code + '\n' + '\n'.join(tests) + '\n}\n')
    return '\n'.join(suites), count


def harness_suite(checks):
    modules, calls = [], 0
    for pattern, code in CODE.items():
        check = checks[pattern]
        cases = check['verificationCases']
        unique = list(dict.fromkeys(c['input'].strip() for c in cases))
        expressions = [call(pattern, text) for text in unique]
        adapter = ('pub fn solve(input: &str) -> String { match input.trim() {\n' + ',\n'.join(r(t) + '=>' + e for t, e in zip(unique, expressions))
                   + ', _=>panic!("fixture adapter has no parser for unseen input") } }\n')
        actual = check['verificationSource'].replace('mod solution;', '', 1).replace('fn main()', 'fn run_actual_harness()', 1)
        corrupt = ',\n'.join('(' + r(c['input']) + ',' + r(c['expectedAnswer']) + ')' for c in cases)
        extra = ''
        if pattern == 'complement-lookup':
            extra = '#[test] fn alternate_valid_pair() { assert!(valid("[6,4,9,7] target=13","0,3","1,2")); assert!(valid("[6,4,9,7] target=13","3,0","1,2")); assert!(!valid("[5,5] target=10","0,0","0,1")); }'
        if pattern == 'peak-search':
            extra = '#[test] fn alternate_peak() { assert!(valid("[1,3,2,4,1]","1","3")); assert!(valid("[1,3,2,4,1]","3","1")); assert!(!valid("[1,3,2,4,1]","2","1")); }'
        if pattern == 'predicate-partition':
            extra = '#[test] fn any_partition_accepted() { assert!(valid("arranged=[2,4,1]","4,2,1","2,4,1")); assert!(!valid("arranged=[1,2]","1,2","2,1")); assert!(!valid("arranged=[1,2]","2,2","2,1")); }'
        modules.append('mod ' + pattern.replace('-', '_') + ' {\nmod solution {\n' + helpers_of(code) + formatting(expressions) + code + adapter + '}\n' + actual
                       + '\n#[test] fn packaged_harness_accepts() { run_actual_harness(); }\n#[test] fn corrupt_results_fail() {\nfor (input,expected) in [' + corrupt
                       + '] { assert!(!valid(input,"INVALID",expected)); }\n}\n' + extra + '\n}\n')
        calls += len(cases)
    return '\n'.join(modules), calls


def standalone(item):
    name, source, expected = item
    path = WORK / 'programs' / f'{name}.rs'
    path.write_text(source)
    binary = WORK / 'programs' / name
    compiled = subprocess.run(['rustc', '--edition=2024', '-A', 'warnings', str(path), '-o', str(binary)], capture_output=True, text=True)
    if compiled.returncode:
        return {'program': name, 'error': compiled.stderr[:600]}
    run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=60)
    formatted = subprocess.run(['rustfmt', '--edition', '2024', '--check', str(path)], capture_output=True, text=True)
    binary.unlink()
    problems = {}
    if run.stdout != expected + '\n':
        problems['output'] = run.stdout + run.stderr[:300]
    if formatted.returncode:
        problems['rustfmt'] = True
    if 'use std::' not in source and 'extern crate' in source:
        problems['extern'] = True
    return {'program': name, **problems} if problems else None


def static_checks():
    problems = []
    def note(where, what):
        problems.append(f'{where}: {what}')
    questions = set()
    for pattern in sorted(CODE):
        check = json.loads((COURSE / 'checks' / f'algorithm.{pattern}.challenge.json').read_text())['challenge']
        tasks = set()
        for stage in ('model', 'recognize', 'challenge'):
            data = lesson(pattern, stage)
            where = data['id']
            before = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:courses/algorithms/lessons/{where}.json'], cwd=REPO, text=True))
            for key in ('id', 'order', 'exerciseKind', 'parentID'):
                if before[key] != data[key]:
                    note(where, f'{key} changed')
            w, a = data['writing'], data['algorithm']
            tasks.add(a['task'])
            questions.add(w['question'])
            if before['writing']['correctAnswer'] != w['correctAnswer']:
                note(where, 'correctAnswer changed')
            if a['rustSketch'] != w['exampleCode']:
                note(where, 'rustSketch differs from exampleCode')
            if len(set(w['answers'])) != 3:
                note(where, 'answers not distinct')
            answer = w['answers'][w['correctAnswer']]
            for text in strings(data):
                if LEAK.search(text):
                    note(where, 'editorial leak')
                for span in BAD_SPANS:
                    if span in text:
                        note(where, f'markup {span}')
            if stage == 'model' and answer.rstrip('.').lower() in w['rule'].lower():
                note(where, 'rule contains the answer')
            if stage != 'model':
                sample = re.search(r'`(.*?)`', w['question'], re.S)[1]
                truth = solve(pattern, sample)
                if answer.strip('`') != truth and not (truth == '' and answer == 'An empty output string'):
                    if pattern not in ('complement-lookup', 'peak-search', 'sorted-two-sum'):
                        note(where, f'marked answer {answer} is not {truth}')
                for i, other in enumerate(w['answers']):
                    if i == w['correctAnswer']:
                        continue
                    if other.strip('`') == truth:
                        note(where, f'distractor {other} is also correct')
                    try:
                        same = [float(x) for x in other.strip('`').split(',')] == [float(x) for x in truth.split(',')]
                    except ValueError:
                        same = False
                    if same:
                        note(where, f'distractor {other} equals the answer numerically')
                    if truth and (other == '`' + truth + '0`' or other.strip('`') == truth[::-1] and len(truth) > 1 and not re.fullmatch(r'[-\d,]+', truth)):
                        note(where, f'mechanical distractor {other}')
            if stage == 'challenge':
                expected = a['expectedAnswer']
                visible = a['visibleInput']
                if len(expected) >= 3:
                    for key in ('summary', 'rule', 'task', 'success'):
                        if expected in w[key]:
                            note(where, f'{key} reveals the answer')
                    if expected in data['concept']:
                        note(where, 'concept reveals the answer')
                    if expected not in visible:
                        for text in [w['explanation'], data['depth']['misconception'], data['depth']['correction'], data['depth']['transferChallenge']] + [s['detail'] for s in data['depth']['traceSteps']]:
                            if expected in text:
                                note(where, 'prose reveals the answer')
                if w['practiceCode'] != check['source']:
                    note(where, 'practiceCode differs from check source')
                if w['task'] != a['task']:
                    note(where, 'writing.task differs from algorithm.task')
        if len(tasks) != 1:
            note(pattern, 'task differs across stages')
        task = tasks.pop()
        starter = (COURSE / 'projects' / f'algorithm.{pattern}.challenge' / 'solution.rs').read_text()
        for name, text in (('source', check['source']), ('solution.rs', starter)):
            if f'// {task}\n' not in text:
                note(pattern, f'{name} comment differs from task')
            for fragment in check['requiredSourceFragments']:
                if fragment not in text:
                    note(pattern, f'{name} lacks {fragment}')
        for fragment in check['forbiddenSourceFragments']:
            if fragment not in check['source']:
                note(pattern, f'starter no longer trips forbidden {fragment}')
        checker = PARTITION_CHECKER if pattern == 'predicate-partition' else checker_of(check['verificationSource'])
        if harness(pattern, check['verificationCases'], checker) != check['verificationSource']:
            note(pattern, 'verificationSource does not match verificationCases')
        for case in check['verificationCases']:
            if case['expectedAnswer'] != solve(pattern, case['input'].strip()):
                note(pattern, f'case {case["input"]!r} disagrees with the oracle')
    if len(questions) != 600:
        note('course', f'{len(questions)} distinct questions')
    return problems


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / 'programs').mkdir(exist_ok=True)
    checks, cases = {}, {}
    for pattern in CODE:
        check = json.loads((COURSE / 'checks' / f'algorithm.{pattern}.challenge.json').read_text())['challenge']
        checks[pattern] = check
        cases[pattern] = list(dict.fromkeys(c['input'].strip() for c in check['verificationCases']))

    reported = []
    for pattern, text, stated in ADDED:
        answer = solve(pattern, text)
        if stated is not None and stated != answer:
            reported.append({'pattern': pattern, 'input': text, 'report': stated, 'oracle': answer})

    programs, seen = [], set()
    for pattern in CODE:
        for stage in ('model', 'recognize', 'challenge'):
            data = lesson(pattern, stage)
            source = data['writing']['exampleCode']
            if stage == 'challenge':
                raw = ANSWER.search(data['writing']['explanation'])[2]
                expected = '' if raw == 'An empty output string' else raw.strip('`')
            else:
                expected = data['algorithm']['expectedAnswer']
                if data['writing']['practiceCode'] != source:
                    print('practiceCode differs', data['id'])
                    raise SystemExit(1)
            if (source, expected) not in seen:
                seen.add((source, expected))
                programs.append((f'{pattern.replace("-", "_")}_{stage}', source, expected))
    with ThreadPoolExecutor(8) as pool:
        failures = [x for x in pool.map(standalone, programs) if x]
    print('standalone programs', len(programs), 'failures', len(failures), failures[:5])

    fuzz = fuzz_inputs(random.Random(20261101))
    source, fixture_count = fixtures_suite(cases, fuzz)
    fixtures_ok, fixtures_result = compile_and_run('fixtures', source)
    print('typed fixtures', fixture_count, fixtures_ok, fixtures_result)

    source, harness_calls = harness_suite(checks)
    harness_ok, harness_result = compile_and_run('harnesses', source)
    print('harnesses', harness_calls, harness_ok, harness_result)

    problems = static_checks()
    print('static problems', len(problems), problems[:30])
    passed = fixtures_ok and harness_ok and not failures and not problems and not reported
    record = {'passed': passed, 'baseline': BASELINE, 'compiler': subprocess.check_output(['rustc', '--version'], text=True).strip(), 'edition': '2024',
              'standalonePrograms': {'count': len(programs), 'failures': failures},
              'typedFixtures': {'count': fixture_count, 'randomDifferentialInputs': sum(map(len, fuzz.values())), 'randomPatterns': sorted(fuzz), 'result': fixtures_result},
              'harnesses': {'patterns': len(checks), 'calls': harness_calls, 'result': harness_result},
              'reportAnswersOverruledByOracle': reported, 'staticProblems': problems,
              'scope': 'Typed known-input adapters, not learner text parsers. Finite fixtures, not a proof for all inputs or of asymptotic bounds.'}
    (BASE / 'atlas-verification.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
