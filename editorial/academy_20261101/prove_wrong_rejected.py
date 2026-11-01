#!/usr/bin/env python3
"""Run every wrong solution named by the audit through the real packaged harness.

Each wrong solution replaces `solution::solve` in the pattern's verificationSource. It
runs against the harness at the baseline commit, where the audit found it passes, and
against the harness in the working tree, where it must fail. A panic and a harness exit
both count as rejection. Run verify_atlas.py for the reference side of the same cases.
"""
import json
import re
import subprocess

from atlas_overlay import BASE, REPO
from apply_pass import BASELINE

WORK = REPO / 'build/academy-20261101/wrong'
ENTRY = re.compile(r'^//@ (\S+) \| (.+)\npub fn (\w+)', re.M)


def harness(source, label, function):
    body = source.replace('mod solution;', '', 1).replace('fn main()', 'pub fn main()', 1)
    return (f'mod {label} {{\nmod solution {{ pub fn solve(input: &str) -> String {{ crate::wrongs::{function}(input.trim()) }} }}\n'
            f'{body}\n}}\n')


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    text = (BASE / 'wrong_solutions.rs').read_text()
    entries = [(m[1], m[2], m[3]) for m in ENTRY.finditer(text)]
    modules, arms = [], []
    for pattern, _, function in entries:
        path = f'courses/algorithms/checks/algorithm.{pattern}.challenge.json'
        before = json.loads(subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=REPO, text=True))['challenge']['verificationSource']
        after = json.loads((REPO / path).read_text())['challenge']['verificationSource']
        for stage, source in (('old', before), ('new', after)):
            label = f'{stage}_{function}'
            modules.append(harness(source, label, function))
            arms.append(f'"{label}" => {label}::main(),')
    program = ('#[allow(dead_code, unused)]\nmod wrongs {\n' + text.replace('#![allow(dead_code, unused)]', '') + '\n}\n' + '\n'.join(modules)
               + 'fn main() { std::panic::set_hook(Box::new(|_| {})); let name = std::env::args().nth(1).unwrap(); match name.as_str() {\n'
               + '\n'.join(arms) + '\n_ => panic!("unknown"), } }\n')
    (WORK / 'all.rs').write_text(program)
    compiled = subprocess.run(['rustc', '--edition=2024', '-A', 'warnings', '-C', 'overflow-checks=off', str(WORK / 'all.rs'), '-o', str(WORK / 'wrong')],
                              capture_output=True, text=True)
    (WORK / 'compile.log').write_text(compiled.stdout + compiled.stderr)
    if compiled.returncode:
        print(compiled.stderr[:12000])
        raise SystemExit(1)
    rows = []
    for pattern, description, function in entries:
        row = {'pattern': pattern, 'function': function, 'description': description}
        for stage in ('old', 'new'):
            run = subprocess.run([str(WORK / 'wrong'), f'{stage}_{function}'], capture_output=True, text=True, timeout=60)
            row['passesBaselineHarness' if stage == 'old' else 'passesExtendedHarness'] = run.returncode == 0
            if stage == 'new':
                row['exit'] = run.returncode
                row['firstFailure'] = run.stderr.strip().splitlines()[0] if run.stderr.strip() else 'panic'
        rows.append(row)
    survivors = [r['function'] for r in rows if r['passesExtendedHarness']]
    summary = {'baseline': BASELINE, 'wrongSolutions': len(rows), 'rejectedByExtendedHarness': len(rows) - len(survivors), 'survivors': survivors,
               'passedBaselineHarness': sum(r['passesBaselineHarness'] for r in rows),
               'failedBaselineHarnessAlready': [r['function'] for r in rows if not r['passesBaselineHarness']],
               'compiler': subprocess.check_output(['rustc', '--version'], text=True).strip(), 'rows': rows}
    (BASE / 'wrong-solution-evidence.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print({k: v for k, v in summary.items() if k != 'rows'})
    raise SystemExit(1 if survivors else 0)


if __name__ == '__main__':
    main()
