"""Atlas pipeline for this pass: the 27 October pipeline plus this pass's changes.

`CODE`, `call` and `solve` supersede the old modules only where a program or an
input grammar changed. The old folder stays importable and unedited.
"""
import ast
from collections import deque
from fractions import Fraction
from functools import lru_cache
import itertools
import math
from pathlib import Path
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
OLD = BASE.parent / 'academy_20261027'
for path in (str(BASE), str(OLD)):
    if path not in sys.path:
        sys.path.insert(0, path)

import fixtures as old_fixtures
import oracles as old_oracles
from fixtures import r, rt, vv
from oracles import array, comma, lists, number, tree, traversal
from programs import PROGRAMS
from rust_sources import CODE as OLD_CODE, HELPERS

CODE = {**OLD_CODE, **PROGRAMS}
CSV = 'fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }\n'
SEMI = 'fn semicolon<T:std::fmt::Display>(a:Vec<Vec<T>>)->String { a.into_iter().map(csv).collect::<Vec<_>>().join(";") }\n'
SOLVED_ROW0 = '534678912'


def _option_list(values):
    return '&[' + ','.join('None' if x is None else f'Some({x})' for x in values) + ']'


def _next_links(text):
    """Return the value array and next links of a list or arena input."""
    values = array(text)
    match = re.search(r'next=(\[[^\]]*\])', text)
    if match:
        return values, ast.literal_eval(match[1].replace('none', 'None'))
    return values, [i + 1 if i + 1 < len(values) else None for i in range(len(values))]


def _walk(next_links, start):
    path, seen, node = [], set(), start
    while node is not None and node not in seen:
        seen.add(node)
        path.append(node)
        node = next_links[node]
    return path


def _intersection_arena(text):
    values, links = _next_links(text)
    return values, _walk(links, number(text, 'a')), _walk(links, number(text, 'b'))


def _keyed(text):
    return [(int(k), v) for k, v in re.findall(r'\((-?\d+),([^,)]+)\)', text)]


def _walls(text):
    return [(int(a), int(b)) for a, b in re.findall(r'\((\d+),(\d+)\)', text.split('walls=')[1])] if 'walls=' in text else []


def _star_ends(text):
    a, b = re.search(r'start=(\d+),(\d+)', text).groups()
    c, d = re.search(r'goal=(\d+),(\d+)', text).groups()
    return (int(a), int(b)), (int(c), int(d))


def _board(text):
    return [[0 if c == '.' else int(c) for c in text.split('=')[1][i:i + 9]] for i in range(0, 81, 9)]


def call(pattern, text):
    text = text.strip()
    match pattern:
        case 'remove-nth-from-end':
            return f'csv(remaining_values(&{r(list(map(int, text.split("->"))))},2))'
        case 'copy-random-list':
            values, links = _next_links(text)
            targets = ast.literal_eval(re.search(r'random=(\[[^\]]*\])', text)[1].replace('null', 'None'))
            return f'copied_pairs(&{r(values)},{_option_list(links)},{_option_list(targets)})'
        case 'rolling-fingerprint':
            return f'window_hash(&{r(array(text))},3).to_string()'
        case 'rolling-window-statistic':
            fn = 'window_variances' if text.startswith('variance=') else 'window_means'
            return f'csv({fn}(&{r(array(text))},3))'
        case 'tree-serialize':
            if text.startswith('data='):
                return f'csv(inorder_values(&deserialize({r(text[5:])})))'
            return f'round_trip(&{rt(tree(text))})'
        case 'a-star':
            start, goal = _star_ends(text)
            return f'grid_a_star(4,4,{r(start)},{r(goal)},&{r(_walls(text))}).map_or("-1".to_string(),|d|d.to_string())'
        case 'sudoku':
            if text.startswith('board='):
                return '{ let mut grid=' + r(_board(text)) + '; assert!(solve_sudoku(&mut grid)); grid.iter().flatten().map(|d|d.to_string()).collect::<String>() }'
        case 'lazy-heap-deletion':
            return f'valid_min(&{r(text.split())}).map_or("none".to_string(),|x|x.to_string())'
        case 'list-cycle':
            values = array(text)
            if 'next=' in text:
                _, links = _next_links(text)
            else:
                tail = text.split('tail->')[1]
                links = [i + 1 for i in range(len(values) - 1)] + ([None if tail == 'none' else int(tail)] if values else [])
            return f'contains_cycle({_option_list(links)}).to_string()'
        case 'list-intersection':
            if 'next=' in text:
                values, a, b = _intersection_arena(text)
                common = 0
                while common < min(len(a), len(b)) and a[-1 - common] == b[-1 - common]:
                    common += 1
                cut = lambda path: path[:len(path) - common]
                shared = a[len(a) - common:]
                pick = lambda nodes: [values[i] for i in nodes]
                return ('{ let tail=shared_list(&' + r(pick(shared)) + ',None); let a=shared_list(&' + r(pick(cut(a))) + ',tail.clone()); let b=shared_list(&'
                        + r(pick(cut(b))) + ',tail); intersection(&a,&b).map_or("none".into(),|x|x.to_string()) }')
        case 'insertion-sort':
            if '(' in text:
                literal = '[' + ','.join(f'({k},{v!r})' for k, v in _keyed(text)) + ']'
                return '{ let mut values=vec!' + literal + '; insertion_sort_by_key(&mut values,|p|p.0); values.iter().map(|(k,v)|format!("{k}{v}")).collect::<Vec<_>>().join(",") }'
        case 'bst-search-insert':
            if 'order=preorder' in text:
                return '{ let mut root=' + rt(tree(text.split(' order=')[0])) + '; insert_bst(&mut root,5); csv(bst_preorder(&root)) }'
        case 'permutations':
            if text.startswith('list='):
                return f'semicolon(permutations(&{r(array(text))}))'
        case 'predicate-partition':
            if text.startswith('arranged='):
                return '{ let mut values=vec!' + r(array(text)) + '; partition_even(&mut values); csv(values) }'
    return old_fixtures.call(pattern, text)


def _bfs_grid(start, goal, walls):
    queue, seen = deque([(start, 0)]), {start}
    while queue:
        (row, col), cost = queue.popleft()
        if (row, col) == goal:
            return cost
        for step in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
            if 0 <= step[0] < 4 and 0 <= step[1] < 4 and step not in walls and step not in seen:
                seen.add(step)
                queue.append((step, cost + 1))
    return -1


def _sudoku_solutions(grid, limit=2):
    """Count and return solutions, picking the most constrained cell first."""
    found = []
    def allowed(row, col):
        used = set(grid[row]) | {grid[i][col] for i in range(9)} | {grid[a][b] for a in range(row // 3 * 3, row // 3 * 3 + 3) for b in range(col // 3 * 3, col // 3 * 3 + 3)}
        return [d for d in range(1, 10) if d not in used]
    def search():
        holes = [(r0, c0) for r0 in range(9) for c0 in range(9) if grid[r0][c0] == 0]
        if not holes:
            found.append([row[:] for row in grid])
            return
        row, col = min(holes, key=lambda cell: len(allowed(*cell)))
        for digit in allowed(row, col):
            grid[row][col] = digit
            search()
            grid[row][col] = 0
            if len(found) >= limit:
                return
    search()
    return found


def solve(pattern, text):
    text = text.strip()
    match pattern:
        case 'variable-window':
            a = array(text)
            return str(min((j - i for i in range(len(a)) for j in range(i + 1, len(a) + 1) if sum(a[i:j]) >= 7), default=0))
        case 'sorted-two-sum':
            a = array(text)
            return comma(next(((i + 1, j + 1) for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] + a[j] == 17), (-1, -1)))
        case 'minimum-cover-window':
            return min((text[i:j] for i in range(len(text)) for j in range(i + 1, len(text) + 1) if set('ABC') <= set(text[i:j])), key=len, default='')
        case 'string-frequency':
            return next((c for c in text if text.count(c) == 1), 'none')
        case 'lazy-heap-deletion':
            values = []
            for token in text.split():
                if token.startswith('push'):
                    values.append(int(token[4:]))
                elif token.startswith('delete'):
                    values.remove(int(token[6:]))
            return str(min(values)) if values else 'none'
        case 'list-cycle':
            values = array(text)
            if 'next=' in text:
                _, links = _next_links(text)
            else:
                tail = text.split('tail->')[1]
                links = [i + 1 for i in range(len(values) - 1)] + ([None if tail == 'none' else int(tail)] if values else [])
            node, seen = (0 if values else None), set()
            while node is not None and node not in seen:
                seen.add(node)
                node = links[node]
            return str(node is not None).lower()
        case 'list-intersection':
            if 'next=' in text:
                values, a, b = _intersection_arena(text)
                return next((str(values[node]) for node in b if node in set(a)), 'none')
        case 'copy-random-list':
            values, links = _next_links(text)
            targets = ast.literal_eval(re.search(r'random=(\[[^\]]*\])', text)[1].replace('null', 'None'))
            order = _walk(links, 0) if values else []
            return comma(f'{values[n]}:{"null" if targets[n] is None else order.index(targets[n])}' for n in order)
        case 'remove-nth-from-end':
            a = text.split('->')
            del a[-2]
            return ','.join(a)
        case 'rolling-fingerprint':
            return str(int(''.join(map(str, array(text)[-3:]))) % 101)
        case 'rolling-window-statistic':
            a = array(text)
            windows = [a[i:i + 3] for i in range(len(a) - 2)]
            if text.startswith('variance='):
                def variance(w):
                    mean = Fraction(sum(w), len(w))
                    return math.floor(sum((x - mean) ** 2 for x in w) / len(w))
                return comma(variance(w) for w in windows)
            return comma(math.floor(Fraction(sum(w), 3)) for w in windows)
        case 'tree-serialize':
            if text.startswith('data='):
                tokens = iter(text[5:].split(','))
                def build():
                    token = next(tokens)
                    if token == '#':
                        return None
                    left = build()
                    right = build()
                    return [int(token), left, right]
                return comma(traversal(build(), 'in'))
        case 'a-star':
            start, goal = _star_ends(text)
            return str(_bfs_grid(start, goal, set(_walls(text))))
        case 'sudoku':
            if text.startswith('board='):
                solutions = _sudoku_solutions(_board(text))
                assert len(solutions) == 1, 'a board fixture must have exactly one solution'
                return ''.join(str(d) for row in solutions[0] for d in row)
        case 'insertion-sort':
            if '(' in text:
                return comma(f'{k}{v}' for k, v in sorted(_keyed(text), key=lambda p: p[0]))
        case 'bst-search-insert':
            if 'order=preorder' in text:
                root = tree(text.split(' order=')[0])
                node, target = root, 5
                while True:
                    side = 1 if target < node[0] else 2
                    if node[side] is None:
                        node[side] = [target, None, None]
                        break
                    node = node[side]
                return comma(traversal(root, 'pre'))
        case 'permutations':
            if text.startswith('list='):
                return ';'.join(comma(p) for p in itertools.permutations(array(text)))
        case 'predicate-partition':
            if text.startswith('arranged='):
                a, boundary = array(text), 0
                for i, x in enumerate(a):
                    if x % 2 == 0:
                        a[boundary], a[i] = a[i], a[boundary]
                        boundary += 1
                evens = sum(x % 2 == 0 for x in a)
                assert all(x % 2 == 0 for x in a[:evens]) and sorted(a) == sorted(array(text))
                return comma(a)
    return old_oracles.solve(pattern, text)


@lru_cache(maxsize=None)
def source(pattern, expression):
    """Format one complete std-only program for a typed call."""
    code = CODE[pattern]
    helpers = ''.join(h for word, h in HELPERS.items() if re.search(r'\b' + word + r'\b', code))
    formatting = (CSV if 'csv(' in expression or 'semicolon(' in expression else '') + (SEMI if 'semicolon(' in expression else '')
    raw = helpers + formatting + code + '\nfn main() {\n    let result = ' + expression + ';\n    println!("{result}");\n}\n'
    return subprocess.run(['rustfmt', '--edition', '2024', '--emit', 'stdout'], input=raw, text=True, capture_output=True, check=True).stdout
