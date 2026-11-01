#!/usr/bin/env python3
"""Rebuild the Algorithm Atlas authoring files for this pass from a fixed baseline.

Reads courses/algorithms at BASELINE from git, applies the tables in edits.py,
adversarial.py and programs.py, and writes the result into the working tree. Running
it twice gives the same files. It does not touch course.json, digests or catalogs.
"""
import io
import json
import re
import tarfile
import subprocess

from atlas_overlay import BASE, CODE, PROGRAMS, REPO, call, r, solve, source
from adversarial import CASES as ADDED
from edits import COMPLEXITY, DISTRACTORS, FACTS, IDEAS, MARKUP, RULES, TASKS, TEXT, USE_CASES
from teaching import FACTS as OLD_FACTS

BASELINE = 'd4e247e'
COURSE = 'courses/algorithms'
STAGES = ('model', 'recognize', 'challenge')
CODE_FIELDS = {'exampleCode', 'rustSketch', 'contentDigest'}
RULE_TAIL = 'State the input preconditions before applying it.'
PARTITION_CHECKER = '''fn valid(input: &str, actual: &str, expected: &str) -> bool {
    if !input.contains("arranged=") { return actual == expected; }
    let parse = |text: &str| -> Option<Vec<i64>> { text.split(',').map(|x| x.trim().parse().ok()).collect() };
    let (Some(got), Some(mut want)) = (parse(actual), parse(expected)) else { return false; };
    let mut sorted = got.clone();
    sorted.sort();
    want.sort();
    let evens = got.iter().take_while(|x| *x % 2 == 0).count();
    sorted == want && got[evens..].iter().all(|x| x % 2 != 0)
}'''
DEFAULT_CHECKER = 'fn valid(_input: &str, actual: &str, expected: &str) -> bool { actual == expected }'


def baseline_files():
    archive = subprocess.check_output(['git', 'archive', BASELINE, COURSE], cwd=REPO)
    with tarfile.open(fileobj=io.BytesIO(archive)) as packed:
        return {entry.name: packed.extractfile(entry).read() for entry in packed if entry.isfile()}


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def rewrite(value, pairs, skip=frozenset()):
    if isinstance(value, str):
        for old, new in pairs:
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [rewrite(x, pairs, skip) for x in value]
    if isinstance(value, dict):
        return {k: (v if k in skip else rewrite(v, pairs, skip)) for k, v in value.items()}
    return value


def fact_pairs(pattern):
    old, new = OLD_FACTS[pattern], FACTS.get(pattern, {})
    pairs = []
    if 'trace' in new:
        pairs.append((old['trace'], new['trace']))
    if 'question' in new:
        pairs.append((old['question'], new['question']))
    if 'correct' in new:
        pairs += [(old['correct'], new['correct']), (old['correct'].lower(), new['correct'].lower())]
    for was, now in zip(old['wrong'], new.get('wrong', old['wrong'])):
        if was != now:
            pairs.append((was, now))
    return pairs


def pattern_pairs(pattern, algorithm):
    pairs = []
    if pattern in TASKS:
        pairs.append((algorithm['task'], TASKS[pattern]))
    if pattern in IDEAS:
        pairs.append((algorithm['idea'], IDEAS[pattern]))
    if pattern in USE_CASES:
        pairs.append((algorithm['useCases'], USE_CASES[pattern]))
    if pattern in COMPLEXITY:
        pairs.append((algorithm['complexity'], COMPLEXITY[pattern]))
    return pairs + fact_pairs(pattern) + TEXT.get(pattern, [])


def harness(pattern, cases, checker):
    entries = ',\n'.join('        (' + r(c['input']) + ',' + r(c['expectedAnswer']) + ')' for c in cases)
    return ('mod solution;\n\n' + checker + '\n\nfn main() {\n    let cases = [\n' + entries
            + '\n    ];\n    for (i,(input,expected)) in cases.iter().enumerate() {\n        let actual = solution::solve(input);\n'
            '        if !valid(input,&actual,expected) { eprintln!("PRIVATE CASE {} FAILED",i+1); std::process::exit(1); }\n    }\n'
            '    println!("PASS ' + pattern + '");\n}\n')


def checker_of(source_text):
    start = source_text.index('fn valid(')
    return source_text[start:source_text.index('\n\nfn main()')]


def teaching_input(lesson):
    return re.search(r'For teaching input `(.*?)`, the worked program returns', lesson['writing']['explanation'], re.S)[1]


def distractor(pattern, stage, index, spec, writing):
    if spec not in ('drop-last', 'reverse-order'):
        return spec
    groups = writing['answers'][writing['correctAnswer']].strip('`').split(';')
    return '`' + ';'.join(groups[:-1] if spec == 'drop-last' else reversed(groups)) + '`'


def main():
    files = baseline_files()
    lessons = {}
    for name, data in files.items():
        if name.startswith(f'{COURSE}/lessons/'):
            lesson = json.loads(data)
            lessons[lesson['id']] = lesson
    added = {}
    for pattern, text, _ in ADDED:
        added.setdefault(pattern, []).append(text)
    case_records, rule_rewrites, leak_tasks = [], [], []

    for pattern in sorted(CODE):
        ids = {stage: f'algorithm.{pattern}.{stage}' for stage in STAGES}
        algorithm = lessons[ids['model']]['algorithm']
        visible = algorithm['visibleInput']
        pairs = pattern_pairs(pattern, algorithm)
        old_task, new_task = algorithm['task'], TASKS.get(pattern, algorithm['task'])

        check_path = f'{COURSE}/checks/algorithm.{pattern}.challenge.json'
        check = json.loads(files[check_path])
        challenge = check['challenge']
        old_cases = challenge['verificationCases']
        new_cases = [{'kind': 'adversarial', 'input': text, 'expectedAnswer': solve(pattern, text)} for text in added.get(pattern, [])]
        cases = old_cases[:-2] + new_cases + old_cases[-2:]
        for case in new_cases:
            case_records.append({'pattern': pattern, **case})
        checker = PARTITION_CHECKER if pattern == 'predicate-partition' else checker_of(challenge['verificationSource'])
        rebuilt = harness(pattern, cases, checker)
        if not new_cases and pattern != 'predicate-partition':
            assert rebuilt == challenge['verificationSource'], pattern
        challenge['verificationCases'] = cases
        challenge['verificationSource'] = rebuilt
        challenge['source'] = challenge['source'].replace(old_task, new_task)
        assert new_task in challenge['source'], pattern
        (REPO / check_path).write_text(dump(check), encoding='utf-8')

        starter_path = f'{COURSE}/projects/algorithm.{pattern}.challenge/solution.rs'
        # Many starter comments still carried a task from before 27 October.
        starter = files[starter_path].decode().split('\n')
        assert starter[1].startswith('    // '), pattern
        starter[1] = '    // ' + new_task
        (REPO / starter_path).write_text('\n'.join(starter), encoding='utf-8')

        for stage in STAGES:
            lesson = lessons[ids[stage]]
            skip = set(CODE_FIELDS) | {'illustration'}
            if stage != 'challenge':
                skip.add('practiceCode')
            teach = teaching_input(lesson) if stage == 'challenge' else visible
            lesson = rewrite(lesson, pairs, skip)
            a, w = lesson['algorithm'], lesson['writing']
            a['task'] = new_task
            if pattern in PROGRAMS:
                program = source(pattern, call(pattern, teach))
                a['rustSketch'] = w['exampleCode'] = program
                if stage != 'challenge':
                    w['practiceCode'] = source(pattern, call(pattern, visible))
            for index, spec in DISTRACTORS.get(stage, {}).get(pattern, {}).items():
                assert index != w['correctAnswer'], (pattern, stage, index)
                w['answers'][index] = distractor(pattern, stage, index, spec, w)
            assert len(set(w['answers'])) == 3, (pattern, stage, w['answers'])
            if stage == 'model':
                answer = w['answers'][w['correctAnswer']]
                if answer.rstrip('.').lower() in w['rule'].lower():
                    w['rule'] = f"{RULES.get(pattern, a['idea'])} {RULE_TAIL}"
                    rule_rewrites.append(pattern)
                    assert answer.rstrip('.').lower() not in w['rule'].lower(), pattern
            if stage == 'challenge' and pattern == 'gray-code':
                step = lesson['depth']['traceSteps'][2]
                step['detail'] = re.sub(r'^For `n=4`, the independently calculated result is `[^`]*`', 'For `n=1`, the independently calculated result is `0,1`', step['detail'])
            lessons[ids[stage]] = lesson

    # Spans around ordinary English, everywhere in the course.
    for lesson_id, lesson in lessons.items():
        lessons[lesson_id] = rewrite(lesson, MARKUP, CODE_FIELDS | {'practiceCode', 'illustration'})

    # Connections repeat a neighbor's title and concept, so rebuild them last.
    for name, data in files.items():
        if name.startswith(f'{COURSE}/units/'):
            ordered = [lessons[i] for i in json.loads(data)['lessonIDs']]
            for i, lesson in enumerate(ordered):
                lesson['depth']['connections'] = [
                    {'direction': direction, 'title': ordered[j]['title'], 'concept': ordered[j]['concept']}
                    for j, direction in ((i - 1, 'previous'), (i + 1, 'next')) if 0 <= j < len(ordered)]

    changed_programs = []
    for name, data in files.items():
        if name.startswith(f'{COURSE}/lessons/'):
            before = json.loads(data)
            lesson = lessons[before['id']]
            for key in ('id', 'order', 'exerciseKind', 'parentID', 'title', 'minutes'):
                assert before[key] == lesson[key], (before['id'], key)
            assert before['writing']['correctAnswer'] == lesson['writing']['correctAnswer']
            if before['writing']['exampleCode'] != lesson['writing']['exampleCode']:
                changed_programs.append(lesson['algorithm']['patternID'])
            (REPO / name).write_text(dump(lesson), encoding='utf-8')

    (BASE / 'changed-programs.json').write_text(dump({
        'baseline': BASELINE,
        'note': 'Patterns whose worked program text changed. Site traces and replay packs must be regenerated for exactly these.',
        'patterns': sorted(set(changed_programs))}), encoding='utf-8')
    (BASE / 'cases-added.json').write_text(dump({
        'baseline': BASELINE, 'casesAdded': len(case_records),
        'patternsTouched': len({c['pattern'] for c in case_records}), 'cases': case_records}), encoding='utf-8')
    (BASE / 'rule-rewrites.json').write_text(dump({
        'baseline': BASELINE, 'modelRulesReworded': len(rule_rewrites),
        'unchanged': sorted(set(CODE) - set(rule_rewrites)), 'patterns': rule_rewrites}), encoding='utf-8')
    print('cases added', len(case_records), '| programs changed', sorted(set(changed_programs)), '| rules', len(rule_rewrites))


if __name__ == '__main__':
    main()
