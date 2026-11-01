// Wrong solutions named by the Atlas audit, ported to the packaged `solve(&str) -> String`
// shape so each one runs against the real harness. Lines that begin `//@` give the
// pattern and description; prove_wrong_rejected.py reads them.
#![allow(dead_code, unused)]
use std::collections::*;

fn j<T: ToString>(v: impl IntoIterator<Item = T>) -> String {
    v.into_iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",")
}
fn v(s: &str) -> Vec<i64> {
    let a = s.find('[').unwrap();
    let b = a + s[a..].find(']').unwrap();
    s[a + 1..b].split(',').filter_map(|x| x.trim().parse().ok()).collect()
}
fn key(s: &str, name: &str) -> i64 {
    let at = s.find(&format!("{name}=")).unwrap() + name.len() + 1;
    let rest = &s[at..];
    let end = rest.find(|c: char| !(c.is_ascii_digit() || c == '-')).unwrap_or(rest.len());
    rest[..end].parse().unwrap()
}
fn pairs(s: &str) -> Vec<(i64, i64)> {
    s.split('(').skip(1).map(|p| {
        let p = &p[..p.find(')').unwrap()];
        let (a, b) = p.split_once(',').unwrap();
        (a.trim().parse().unwrap(), b.trim().parse().unwrap())
    }).collect()
}
fn upairs(s: &str) -> Vec<(usize, usize)> {
    pairs(s).into_iter().map(|(a, b)| (a as usize, b as usize)).collect()
}
fn und(n: usize, e: &[(usize, usize)]) -> Vec<Vec<usize>> {
    let mut g = vec![vec![]; n];
    for &(a, b) in e { g[a].push(b); g[b].push(a); }
    g
}
fn dir(n: usize, e: &[(usize, usize)]) -> Vec<Vec<usize>> {
    let mut g = vec![vec![]; n];
    for &(a, b) in e { g[a].push(b); }
    g
}
fn weighted(s: &str) -> Vec<(usize, usize, i64)> {
    let s = s.strip_prefix("edges=").unwrap_or(s);
    s.split(',').map(|e| {
        let (ends, w) = e.split_once(':').unwrap();
        let (a, b) = ends.split_once("->").or_else(|| ends.split_once('-')).unwrap();
        (a.parse().unwrap(), b.parse().unwrap(), w.parse().unwrap())
    }).collect()
}
fn arrows(s: &str) -> Vec<(usize, usize)> {
    let s = s.split("edges=").nth(1).unwrap_or(s);
    s.split(',').map(|e| { let (a, b) = e.split_once("->").unwrap(); (a.parse().unwrap(), b.parse().unwrap()) }).collect()
}
fn count_n(e: &[(usize, usize, i64)]) -> usize { e.iter().map(|x| x.0.max(x.1)).max().unwrap() + 1 }
fn tokens(s: &str) -> Vec<Option<i64>> {
    let a = s.find('[').unwrap();
    let b = a + s[a..].find(']').unwrap();
    s[a + 1..b].split(',').map(|t| t.trim().parse().ok()).collect()
}
// A compact level-order tree as (value, left, right) rows.
fn tree(s: &str) -> Vec<(i64, Option<usize>, Option<usize>)> {
    let t = tokens(s);
    if t.is_empty() { return vec![]; }
    let mut rows = vec![(t[0].unwrap(), None, None)];
    let mut queue = VecDeque::from([0usize]);
    let mut i = 1;
    while i < t.len() {
        let p = queue.pop_front().unwrap();
        for side in 0..2 {
            if i < t.len() {
                if let Some(x) = t[i] {
                    rows.push((x, None, None));
                    let id = rows.len() - 1;
                    if side == 0 { rows[p].1 = Some(id) } else { rows[p].2 = Some(id) }
                    queue.push_back(id);
                }
                i += 1;
            }
        }
    }
    rows
}
fn height(t: &[(i64, Option<usize>, Option<usize>)], n: Option<usize>) -> usize {
    n.map_or(0, |i| 1 + height(t, t[i].1).max(height(t, t[i].2)))
}
fn matrix(s: &str) -> Vec<Vec<i64>> {
    let a = s.find("[[").unwrap();
    let body = &s[a + 1..s.rfind("]]").unwrap() + 1];
    body.split("],").map(|row| row.trim_matches(|c| c == '[' || c == ']').split(',')
        .map(|x| x.trim().parse().unwrap_or(999_999_999)).collect()).collect()
}

// ---- Report 1
//@ linear-scan | returns the last negative index
pub fn linear_last_negative(s: &str) -> String { let a = v(s); a.iter().rposition(|&x| x < 0).map_or(-1, |i| i as i64).to_string() }
//@ predicate-partition | counts evens and never partitions
pub fn predicate_count_only(s: &str) -> String { v(s).iter().filter(|x| *x % 2 == 0).count().to_string() }
//@ boyer-moore-majority | returns the first element
pub fn boyer_first(s: &str) -> String { v(s)[0].to_string() }
//@ floyd-state-cycle | returns next of the last index
pub fn floyd_next_of_last(s: &str) -> String { v(s).last().unwrap().to_string() }
//@ hash-membership | checks only whether the last value appeared earlier
pub fn hash_member_last(s: &str) -> String { let a = v(s); a[..a.len() - 1].contains(a.last().unwrap()).to_string() }
//@ hash-frequency | compares length plus letter set
pub fn hash_freq_letterset(s: &str) -> String {
    let (a, b) = s.split_once("; ").unwrap();
    let f = |x: &str| x.bytes().collect::<BTreeSet<_>>();
    (a.len() == b.len() && f(a) == f(b)).to_string()
}
//@ group-by-key | keys on the letter set
pub fn group_letterset(s: &str) -> String {
    let mut m: HashMap<BTreeSet<u8>, usize> = HashMap::new();
    for w in s.trim_matches(|c| c == '[' || c == ']').split(',') { *m.entry(w.bytes().collect()).or_default() += 1; }
    m.values().max().unwrap().to_string()
}
//@ index-map | keeps the earliest index of each value
pub fn index_map_earliest(s: &str) -> String {
    let a = v(s); let mut m = HashMap::new(); let mut best = -1i64;
    for (i, &x) in a.iter().enumerate() {
        match m.get(&x) { Some(&k) => { let d = (i - k) as i64; if best < 0 || d < best { best = d } } None => { m.insert(x, i); } }
    }
    best.to_string()
}
//@ coordinate-compression | omits deduplication
pub fn coord_no_dedup(s: &str) -> String {
    let a = v(s); let mut k = a.clone(); k.sort();
    j(a.iter().map(|x| k.iter().position(|y| y == x).unwrap()))
}
//@ longest-consecutive-set | sorts and resets the run on a duplicate
pub fn longest_sort_reset(s: &str) -> String {
    let mut a = v(s); a.sort(); let (mut b, mut c) = (1, 1);
    for w in a.windows(2) { if w[1] == w[0] + 1 { c += 1 } else { c = 1 } b = b.max(c) }
    b.to_string()
}
//@ bidirectional-map | compares distinct counts only
pub fn bimap_distinct_counts(s: &str) -> String {
    let (p, w) = s.split_once("; ").unwrap(); let w: Vec<_> = w.split(' ').collect();
    (p.len() == w.len() && p.bytes().collect::<HashSet<_>>().len() == w.iter().collect::<HashSet<_>>().len()).to_string()
}
//@ randomized-set | does not update the moved value's index
pub fn randset_no_index_update(s: &str) -> String {
    let mut val: Vec<i64> = vec![]; let mut idx: HashMap<i64, usize> = HashMap::new();
    for t in s.split(' ') {
        if let Some(n) = t.strip_prefix("add") { let n: i64 = n.parse().unwrap(); if !idx.contains_key(&n) { idx.insert(n, val.len()); val.push(n); } }
        else { let n: i64 = t[6..].parse().unwrap(); if let Some(i) = idx.remove(&n) { val.swap_remove(i); } }
    }
    val.sort(); j(val)
}
//@ prefix-suffix-product | divides the total product
pub fn prod_division(s: &str) -> String { let a = v(s); let p: i64 = a.iter().product(); j(a.iter().map(|x| p / x)) }
//@ prefix-xor | hard-codes the visible answer
pub fn prefix_xor_hardcode(s: &str) -> String { (if v(s)[0] == 5 { 7 } else { 0 }).to_string() }
//@ equilibrium-index | returns the last match
pub fn equilibrium_last(s: &str) -> String {
    let a = v(s); let t: i64 = a.iter().sum(); let (mut r, mut l) = (-1i64, 0);
    for (i, x) in a.iter().enumerate() { if l == t - l - x { r = i as i64 } l += x }
    r.to_string()
}
//@ opposite-ends | tests only the two ends
pub fn opposite_ends_only(s: &str) -> String { let a = v(s); (a[0] + a[a.len() - 1] == 10).to_string() }
//@ three-sum | omits endpoint skipping
pub fn three_sum_no_skip(s: &str) -> String {
    let mut a = v(s); a.sort(); let mut c = 0;
    for i in 0..a.len().saturating_sub(2) {
        if i > 0 && a[i] == a[i - 1] { continue }
        let (mut l, mut r) = (i + 1, a.len() - 1);
        while l < r { let t = a[i] + a[l] + a[r]; if t < 0 { l += 1 } else if t > 0 { r -= 1 } else { c += 1; l += 1; r -= 1 } }
    }
    c.to_string()
}
//@ sorted-two-sum | panics when no pair exists
pub fn sorted_two_sum_panic(s: &str) -> String {
    let a = v(s); let (mut l, mut r) = (0, a.len() - 1);
    loop { assert!(l < r); let t = a[l] + a[r]; if t == 17 { break format!("{},{}", l + 1, r + 1) } if t < 17 { l += 1 } else { r -= 1 } }
}
//@ fixed-window | starts the best sum at zero
pub fn fixed_window_zero(s: &str) -> String { let a = v(s); let mut b = 0; for w in a.windows(3) { b = b.max(w.iter().sum::<i64>()) } b.to_string() }
//@ variable-window | sorts descending and sums greedily
pub fn variable_greedy(s: &str) -> String {
    let mut a = v(s); a.sort(); a.reverse(); let (mut t, mut c) = (0, 0);
    for x in a { if t >= 7 { break } t += x; c += 1 }
    c.to_string()
}
//@ unique-window | counts distinct characters
pub fn unique_distinct(s: &str) -> String { s.bytes().collect::<HashSet<_>>().len().to_string() }
//@ rolling-window-statistic | returns the middle element of each window
pub fn rolling_middle(s: &str) -> String { let a = v(s); j(a.windows(3).map(|w| w[1])) }
//@ rolling-window-statistic | rounds the mean at each update
pub fn rolling_round_each(s: &str) -> String {
    let a = v(s); let mut m = (a[0] + a[1] + a[2]) / 3; let mut o = vec![m];
    for i in 3..a.len() { m += (a[i] - a[i - 3]) / 3; o.push(m) }
    j(o)
}
//@ rolling-fingerprint | folds the whole input with no window, the old program
pub fn rolling_whole_fold(s: &str) -> String { let mut h = 0; for d in v(s) { h = (h * 10 + d) % 101 } h.to_string() }
//@ in-place-merge | ignores m and treats zeros as empty slots
pub fn merge_zeros_empty(s: &str) -> String {
    let a = v(s); let b = v(s.split("b=").nth(1).unwrap());
    let mut r: Vec<i64> = a.into_iter().filter(|x| *x != 0).chain(b).collect(); r.sort(); j(r)
}
//@ minimum-cover-window | returns the input when no cover exists
pub fn min_cover_whole(s: &str) -> String {
    let b = s.as_bytes(); let mut best: Option<&str> = None;
    for i in 0..b.len() {
        let mut seen = [false; 3];
        for k in i..b.len() {
            if b[k] >= b'A' && b[k] <= b'C' { seen[(b[k] - b'A') as usize] = true }
            if seen == [true; 3] { if best.map_or(true, |x| k + 1 - i < x.len()) { best = Some(&s[i..=k]) } break }
        }
    }
    best.unwrap_or(s).to_string()
}
//@ min-max-tracking | subtracts in i32, the old program under -O
pub fn spread_i32(s: &str) -> String {
    let a: Vec<i32> = v(s).into_iter().map(|x| x as i32).collect();
    let (l, h) = (*a.iter().min().unwrap(), *a.iter().max().unwrap());
    h.wrapping_sub(l).to_string()
}

// ---- Report 2
//@ tree-height-balance | checks only the root
pub fn balance_root_only(s: &str) -> String {
    let t = tree(s); let (a, b) = (height(&t, t[0].1), height(&t, t[0].2));
    (a.abs_diff(b) <= 1).to_string()
}
//@ tree-diameter | assumes the longest path passes through the root
pub fn diameter_root_only(s: &str) -> String { let t = tree(s); (height(&t, t[0].1) + height(&t, t[0].2)).to_string() }
//@ tree-inorder | sorts the tokens without building a tree
pub fn inorder_sorted(s: &str) -> String { let mut a = v(s); a.sort(); j(a) }
//@ bst-search-insert | appends 5 and sorts, with no BST
pub fn bst_sort_append(s: &str) -> String { let mut a = v(s); a.push(5); a.sort(); j(a) }
//@ lowest-common-ancestor | answers 5 if 1 is under 5, otherwise the root
pub fn lca_five_or_root(s: &str) -> String {
    let t = tree(s);
    let five = t.iter().position(|n| n.0 == 5).unwrap();
    fn under(t: &[(i64, Option<usize>, Option<usize>)], n: Option<usize>) -> bool {
        n.is_some_and(|i| t[i].0 == 1 || under(t, t[i].1) || under(t, t[i].2))
    }
    (if under(&t, t[five].1) || under(&t, t[five].2) { 5 } else { t[0].0 }).to_string()
}
//@ list-cycle | reads the answer from the text: no "none" means a cycle
pub fn cycle_no_none(s: &str) -> String { (!s.contains("none")).to_string() }
//@ list-cycle | checks the literal "index 1" wording
pub fn cycle_tail_one(s: &str) -> String { s.contains("tail->1").to_string() }
//@ list-cycle | compares values instead of node identity
pub fn cycle_values(s: &str) -> String {
    let a = v(s);
    let tail: Option<usize> = s.rsplit("tail->").next().unwrap().parse().ok();
    let nx = |i: usize| if i + 1 < a.len() { Some(i + 1) } else { tail };
    let (mut p, mut q) = (Some(0usize), Some(0usize));
    loop {
        p = p.and_then(nx); q = q.and_then(nx).and_then(nx);
        match (p, q) { (_, None) => return "false".into(), (Some(x), Some(y)) if a[x] == a[y] => return "true".into(), _ => {} }
    }
}
//@ list-intersection | prints shared[0] with no lists
pub fn intersection_shared_first(s: &str) -> String { let i = s.find("shared=").unwrap(); v(&s[i + 7..]).first().map_or("none".into(), |x| x.to_string()) }
//@ copy-random-list | zips the input strings with no copy
pub fn copy_zip(s: &str) -> String {
    let parts: Vec<&str> = s.split(" random=").collect();
    let a = parts[0].trim_start_matches("values=").trim_matches(|c| c == '[' || c == ']');
    let r = parts[1].trim_matches(|c| c == '[' || c == ']');
    a.split(',').zip(r.split(',')).map(|(x, y)| format!("{x}:{y}")).collect::<Vec<_>>().join(",")
}
fn lb(a: &[i64], t: i64) -> usize { a.partition_point(|&x| x < t) }
//@ binary-exact | indexes a[lo] unchecked
pub fn binary_unchecked(s: &str) -> String { let a = v(s); let i = lb(&a, 9); if a[i] == 9 { i.to_string() } else { "-1".into() } }
//@ first-last-position | indexes a[first] unchecked
pub fn first_last_unchecked(s: &str) -> String {
    let a = v(s); let i = lb(&a, 8);
    if a[i] != 8 { "-1,-1".into() } else { format!("{},{}", i, a.partition_point(|&x| x <= 8) - 1) }
}
//@ lower-bound | off by one with hi=len-1
pub fn lower_bound_hi(s: &str) -> String {
    let a = v(s); let (mut lo, mut hi) = (0, a.len() - 1);
    while lo < hi { let m = (lo + hi) / 2; if a[m] < 4 { lo = m + 1 } else { hi = m } }
    lo.to_string()
}
//@ radix-sort | fixed three decimal passes
pub fn radix_three_passes(s: &str) -> String { let mut a = v(s); for d in [1, 10, 100] { a.sort_by_key(|x| x / d % 10); } j(a) }
//@ insertion-sort | unstable shift with >=
pub fn insertion_unstable(s: &str) -> String {
    if s.contains('(') {
        let mut a: Vec<(i64, &str)> = s.split('(').skip(1).map(|p| { let p = &p[..p.find(')').unwrap()]; let (k, l) = p.split_once(',').unwrap(); (k.parse().unwrap(), l) }).collect();
        for i in 1..a.len() { let x = a[i]; let mut k = i; while k > 0 && a[k - 1].0 >= x.0 { a[k] = a[k - 1]; k -= 1; } a[k] = x; }
        return a.iter().map(|(k, l)| format!("{k}{l}")).collect::<Vec<_>>().join(",");
    }
    let mut a = v(s);
    for i in 1..a.len() { let x = a[i]; let mut k = i; while k > 0 && a[k - 1] >= x { a[k] = a[k - 1]; k -= 1; } a[k] = x; }
    j(a)
}
//@ selection-sort | formula ceil(misplaced/2) with no sort
pub fn selection_formula(s: &str) -> String { let a = v(s); let mut b = a.clone(); b.sort(); a.iter().zip(&b).filter(|(x, y)| x != y).count().div_ceil(2).to_string() }

// ---- Report 3
//@ priority-scheduling | sorts by arrival, duration, id with no simulation
pub fn sched_sorted(s: &str) -> String {
    let mut jobs: Vec<(i64, i64, i64)> = s.split("(id").skip(1).map(|p| {
        let p = &p[..p.find(')').unwrap()];
        let f: Vec<&str> = p.split(',').collect();
        (f[1][1..].parse().unwrap(), f[2][1..].parse().unwrap(), f[0].parse().unwrap())
    }).collect();
    jobs.sort(); j(jobs.iter().map(|x| x.2))
}
//@ adjacency-list | omits the neighbor sort
pub fn adj_no_sort(s: &str) -> String { j(und(key(s, "n") as usize, &upairs(s))[2].clone()) }
//@ graph-bfs | uses DFS depth as the distance
pub fn bfs_dfs_depth(s: &str) -> String {
    let n = key(s, "n") as usize; let g = und(n, &upairs(s)); let mut d = vec![-1; n];
    fn go(x: usize, de: i64, g: &[Vec<usize>], d: &mut Vec<i64>) { d[x] = de; for &u in &g[x] { if d[u] == -1 { go(u, de + 1, g, d) } } }
    go(0, 0, &g, &mut d); j(d)
}
//@ graph-bfs | parses edges as directed
pub fn bfs_directed(s: &str) -> String {
    let n = key(s, "n") as usize; let g = dir(n, &upairs(s)); let mut d = vec![-1i64; n]; d[0] = 0;
    let mut q = VecDeque::from([0usize]);
    while let Some(x) = q.pop_front() { for &u in &g[x] { if d[u] < 0 { d[u] = d[x] + 1; q.push_back(u); } } }
    j(d)
}
//@ graph-dfs | parses edges as directed
pub fn dfs_directed(s: &str) -> String {
    let e = upairs(s); let n = e.iter().map(|x| x.0.max(x.1)).max().map_or(1, |m| m + 1);
    let mut g = dir(n, &e); for x in &mut g { x.sort(); }
    let mut seen = vec![false; n]; let mut o = vec![];
    fn go(x: usize, g: &[Vec<usize>], seen: &mut Vec<bool>, o: &mut Vec<usize>) { seen[x] = true; o.push(x); for &u in &g[x] { if !seen[u] { go(u, g, seen, o) } } }
    go(0, &g, &mut seen, &mut o); j(o)
}
//@ connected-components | computes n minus the edge count
pub fn components_formula(s: &str) -> String { (key(s, "n") - pairs(s).len() as i64).to_string() }
//@ bipartite-coloring | colors from node 0 only
pub fn bipartite_single(s: &str) -> String {
    let n = key(s, "n") as usize; let g = und(n, &upairs(s)); let mut c = vec![None; n]; c[0] = Some(false);
    let mut q = VecDeque::from([0usize]);
    while let Some(x) = q.pop_front() { for &u in &g[x] { if c[u] == c[x] { return "false".into(); } if c[u].is_none() { c[u] = Some(!c[x].unwrap()); q.push_back(u); } } }
    "true".into()
}
//@ undirected-cycle | runs DFS from node 0 only
pub fn cycle_single(s: &str) -> String {
    let e = upairs(s); let n = e.iter().map(|x| x.0.max(x.1)).max().unwrap() + 1; let g = und(n, &e);
    fn go(x: usize, p: usize, g: &[Vec<usize>], seen: &mut Vec<bool>) -> bool { seen[x] = true; for &u in &g[x] { if u != p && (seen[u] || go(u, x, g, seen)) { return true; } } false }
    go(0, n, &g, &mut vec![false; n]).to_string()
}
//@ kahn-topological | uses a FIFO queue
pub fn kahn_fifo(s: &str) -> String {
    let n = key(s, "n") as usize; let e = arrows(s); let g = dir(n, &e); let mut d = vec![0; n];
    for &(_, b) in &e { d[b] += 1; }
    let mut q: VecDeque<usize> = (0..n).filter(|&x| d[x] == 0).collect(); let mut o = vec![];
    while let Some(x) = q.pop_front() { o.push(x); for &u in &g[x] { d[u] -= 1; if d[u] == 0 { q.push_back(u); } } }
    j(o)
}
//@ dfs-topological | omits the neighbor sort
pub fn dfs_topo_no_sort(s: &str) -> String {
    let n = key(s, "n") as usize; let g = dir(n, &arrows(s)); let mut c = vec![false; n]; let mut o = vec![];
    fn go(x: usize, g: &[Vec<usize>], c: &mut Vec<bool>, o: &mut Vec<usize>) { c[x] = true; for &u in &g[x] { if !c[u] { go(u, g, c, o) } } o.push(x); }
    for x in 0..n { if !c[x] { go(x, &g, &mut c, &mut o) } }
    o.reverse(); j(o)
}
fn show(d: &[i64]) -> Vec<i64> { d.iter().map(|&x| if x == i64::MAX { -1 } else { x }).collect() }
fn one_pass(n: usize, e: &[(usize, usize, i64)], both: bool) -> Vec<i64> {
    let mut d = vec![i64::MAX; n]; d[0] = 0;
    for &(a, b, w) in e {
        if d[a] != i64::MAX && d[a] + w < d[b] { d[b] = d[a] + w; }
        if both && d[b] != i64::MAX && d[b] + w < d[a] { d[a] = d[b] + w; }
    }
    show(&d)
}
fn finalized(n: usize, e: &[(usize, usize, i64)]) -> Vec<i64> {
    let mut g = vec![vec![]; n]; for &(a, b, w) in e { g[a].push((b, w)); }
    let (mut d, mut done, mut h) = (vec![i64::MAX; n], vec![false; n], BinaryHeap::new());
    d[0] = 0; h.push(std::cmp::Reverse((0i64, 0usize)));
    while let Some(std::cmp::Reverse((c, x))) = h.pop() {
        if done[x] { continue; } done[x] = true;
        for &(u, w) in &g[x] { if !done[u] && c + w < d[u] { d[u] = c + w; h.push(std::cmp::Reverse((d[u], u))); } }
    }
    show(&d)
}
//@ dijkstra | one relaxation pass in listed order
pub fn dijkstra_one_pass(s: &str) -> String { let e = weighted(s); j(one_pass(count_n(&e), &e, true)) }
//@ dijkstra | parses edges as directed
pub fn dijkstra_directed(s: &str) -> String { let e = weighted(s); j(finalized(count_n(&e), &e)) }
//@ zero-one-bfs | one relaxation pass in listed order
pub fn zero_one_one_pass(s: &str) -> String { let e = weighted(s); one_pass(count_n(&e).max(4), &e, true)[3].to_string() }
//@ bellman-ford | one pass in listed order
pub fn bellman_one_pass(s: &str) -> String { let e = weighted(s); j(one_pass(count_n(&e), &e, false)) }
//@ bellman-ford | Dijkstra with finalized nodes
pub fn bellman_finalized(s: &str) -> String { let e = weighted(s); j(finalized(count_n(&e), &e)) }
//@ dag-shortest-path | Dijkstra with finalized nodes
pub fn dag_finalized(s: &str) -> String { let e = weighted(s); finalized(count_n(&e).max(5), &e)[4].to_string() }
//@ floyd-warshall | min of the direct edge and one two-hop route
pub fn floyd_two_hop(s: &str) -> String { let m = matrix(s); m[0][2].min(m[0][1].saturating_add(m[1][2])).to_string() }
//@ floyd-warshall | the classic k-innermost loop
pub fn floyd_k_inner(s: &str) -> String {
    let mut d = matrix(s); let n = d.len(); const I: i64 = 999_999_999;
    for i in 0..n { for k2 in 0..n { for k in 0..n { if d[i][k] != I && d[k][k2] != I { d[i][k2] = d[i][k2].min(d[i][k] + d[k][k2]); } } } }
    d[0][2].to_string()
}
//@ dinic-max-flow | augments without reverse edges
pub fn flow_no_reverse(s: &str) -> String {
    let e = weighted(s); let n = count_n(&e).max(4); let mut c = vec![vec![0i64; n]; n];
    for &(a, b, w) in &e { c[a][b] += w; }
    let mut total = 0;
    loop {
        fn go(x: usize, c: &[Vec<i64>], seen: &mut Vec<bool>, path: &mut Vec<usize>) -> bool {
            seen[x] = true; path.push(x); if x == 3 { return true; }
            for u in 0..c.len() { if c[x][u] > 0 && !seen[u] && go(u, c, seen, path) { return true; } }
            path.pop(); false
        }
        let mut path = vec![];
        if !go(0, &c, &mut vec![false; n], &mut path) { return total.to_string(); }
        let m = path.windows(2).map(|w| c[w[0]][w[1]]).min().unwrap();
        for w in path.windows(2) { c[w[0]][w[1]] -= m; }
        total += m;
    }
}
//@ dinic-max-flow | min of source capacity and sink capacity
pub fn flow_cut(s: &str) -> String {
    let e = weighted(s);
    let a: i64 = e.iter().filter(|x| x.0 == 0).map(|x| x.2).sum();
    let b: i64 = e.iter().filter(|x| x.1 == 3).map(|x| x.2).sum();
    a.min(b).to_string()
}
//@ word-grid-search | never unmarks a visited cell
pub fn word_no_unmark(s: &str) -> String {
    let (g, w) = s.strip_prefix("grid=").unwrap().split_once(" word=").unwrap();
    let g: Vec<Vec<u8>> = g.split(',').map(|r| r.bytes().collect()).collect(); let w = w.as_bytes();
    let mut seen = vec![vec![false; g[0].len()]; g.len()];
    fn go(g: &[Vec<u8>], w: &[u8], r: usize, c: usize, i: usize, s: &mut Vec<Vec<bool>>) -> bool {
        if s[r][c] || g[r][c] != w[i] { return false; }
        if i + 1 == w.len() { return true; }
        s[r][c] = true;
        for (dr, dc) in [(-1isize, 0isize), (1, 0), (0, -1), (0, 1)] {
            let (a, b) = (r as isize + dr, c as isize + dc);
            if a >= 0 && b >= 0 && a < g.len() as isize && b < g[0].len() as isize && go(g, w, a as usize, b as usize, i + 1, s) { return true; }
        }
        false
    }
    for r in 0..g.len() { for c in 0..g[0].len() { if go(&g, w, r, c, 0, &mut seen) { return "true".into(); } } }
    "false".into()
}
//@ activity-selection | shortest interval first
pub fn activity_shortest(s: &str) -> String {
    let mut a = pairs(s); a.sort_by_key(|&(x, y)| (y - x, x)); let mut k: Vec<(i64, i64)> = vec![];
    for (x, y) in a { if k.iter().all(|&(p, q)| y <= p || x >= q) { k.push((x, y)); } }
    k.len().to_string()
}
//@ merge-intervals | omits the sort
pub fn merge_no_sort(s: &str) -> String {
    let mut o: Vec<(i64, i64)> = vec![];
    for (x, y) in pairs(s) { if let Some(l) = o.last_mut() { if x <= l.1 { l.1 = l.1.max(y); continue; } } o.push((x, y)); }
    o.iter().map(|(a, b)| format!("{a}-{b}")).collect::<Vec<_>>().join(",")
}
//@ jump-game | always takes the maximum jump
pub fn jump_max_step(s: &str) -> String {
    let a = v(s); let mut i = 0;
    loop { if i >= a.len() - 1 { return "true".into(); } if a[i] == 0 { return "false".into(); } i += a[i] as usize; }
}
//@ minimum-arrows | sorts by start and keeps the first end without shrinking
pub fn arrows_no_shrink(s: &str) -> String {
    let mut a = pairs(s); a.sort(); let (mut l, mut c) = (None, 0);
    for (x, y) in a { if l.is_none_or(|p| x > p) { c += 1; l = Some(y); } }
    c.to_string()
}
//@ meeting-rooms-heap | compares only with the last-added meeting's end
pub fn rooms_last(s: &str) -> String {
    let mut a = pairs(s); a.sort(); let (mut r, mut last) = (0, i64::MIN);
    for (x, y) in a { if r == 0 || last > x { r += 1; } last = y; }
    r.to_string()
}
//@ a-star | the one-line Manhattan formula, with no search
pub fn a_star_manhattan(s: &str) -> String {
    let n: Vec<i64> = s.split(|c: char| !c.is_ascii_digit()).filter(|x| !x.is_empty()).map(|x| x.parse().unwrap()).collect();
    ((n[0] - n[2]).abs() + (n[1] - n[3]).abs()).to_string()
}
//@ sudoku | 45 minus the digit sum, with no backtracking
pub fn sudoku_sum(s: &str) -> String { (45 - s.split('=').nth(1).unwrap().bytes().filter(u8::is_ascii_digit).map(|b| (b - b'0') as i64).sum::<i64>()).to_string() }
//@ permutations | n factorial, with no enumeration
pub fn permutations_factorial(s: &str) -> String { (1..=v(s).len() as u64).product::<u64>().to_string() }

// ---- Report 4
//@ house-robber | takes the largest remaining value and drops its neighbours
pub fn robber_greedy(s: &str) -> String {
    let a = v(s); let mut alive = vec![true; a.len()]; let mut t = 0;
    loop {
        let mut b: Option<usize> = None;
        for i in 0..a.len() { if alive[i] && b.map_or(true, |k| a[i] > a[k]) { b = Some(i) } }
        let Some(i) = b else { break };
        t += a[i]; alive[i] = false;
        if i > 0 { alive[i - 1] = false } if i + 1 < a.len() { alive[i + 1] = false }
    }
    t.to_string()
}
//@ word-break-dp | greedy longest prefix
pub fn word_break_greedy(s: &str) -> String {
    let (t, d) = s.strip_prefix("text=").unwrap().split_once(" dict=[").unwrap();
    let d: Vec<&str> = d.trim_end_matches(']').split(',').collect(); let mut r = t;
    while !r.is_empty() {
        match d.iter().filter(|w| r.starts_with(**w)).max_by_key(|w| w.len()) { Some(w) => r = &r[w.len()..], None => return "false".into() }
    }
    "true".into()
}
//@ decode-ways | accepts any two-digit pair with a nonzero tens digit
pub fn decode_any_pair(s: &str) -> String {
    let a = s.as_bytes(); let (mut b, mut c) = (1u64, 1u64);
    for i in 0..a.len() { let mut n = if a[i] != b'0' { c } else { 0 }; if i > 0 && a[i - 1] != b'0' { n += b } b = c; c = n }
    c.to_string()
}
//@ subset-sum | checks only subsets of size at most two
pub fn subset_two(s: &str) -> String {
    let a = v(s);
    (a.iter().any(|&x| x == 11) || (0..a.len()).any(|i| (i + 1..a.len()).any(|k| a[i] + a[k] == 11))).to_string()
}
//@ edit-distance | max length minus LCS
pub fn edit_via_lcs(s: &str) -> String {
    let (a, b) = s.split_once(" -> ").unwrap(); let (a, b) = (a.as_bytes(), b.as_bytes());
    let mut d = vec![vec![0usize; b.len() + 1]; a.len() + 1];
    for i in 0..a.len() { for k in 0..b.len() { d[i + 1][k + 1] = if a[i] == b[k] { d[i][k] + 1 } else { d[i][k + 1].max(d[i + 1][k]) } } }
    (a.len().max(b.len()) - d[a.len()][b.len()]).to_string()
}
//@ matrix-chain | left-to-right fold, with no DP
pub fn matrix_fold(s: &str) -> String { let d = v(s); (1..d.len().saturating_sub(1)).map(|i| d[0] * d[i] * d[i + 1]).sum::<i64>().to_string() }
//@ bitmask-dp | nearest neighbour tour
pub fn tsp_nearest(s: &str) -> String {
    let c = matrix(s); let n = c.len(); let mut seen = vec![false; n]; seen[0] = true; let (mut cur, mut t) = (0, 0);
    for _ in 1..n { let nx = (0..n).filter(|&k| !seen[k]).min_by_key(|&k| c[cur][k]).unwrap(); t += c[cur][nx]; seen[nx] = true; cur = nx }
    (t + c[cur][0]).to_string()
}
//@ tree-dp | max of even-level sum and odd-level sum
pub fn tree_levels(s: &str) -> String {
    let t = tree(s); let mut q = VecDeque::from([(0usize, 0)]); let (mut even, mut odd) = (0, 0);
    while let Some((i, l)) = q.pop_front() {
        if l % 2 == 0 { even += t[i].0 } else { odd += t[i].0 }
        if let Some(x) = t[i].1 { q.push_back((x, l + 1)); } if let Some(x) = t[i].2 { q.push_back((x, l + 1)); }
    }
    even.max(odd).to_string()
}
//@ string-frequency | falls back to the first character
pub fn frequency_fallback(s: &str) -> String { s.chars().find(|&c| s.matches(c).count() == 1).unwrap_or(s.chars().next().unwrap()).to_string() }
//@ string-two-pointers | keeps alphabetic characters only
pub fn palindrome_alpha(s: &str) -> String {
    let a: Vec<u8> = s.bytes().filter(|c| c.is_ascii_alphabetic()).map(|c| c.to_ascii_lowercase()).collect();
    a.iter().eq(a.iter().rev()).to_string()
}
//@ run-length-encoding | a single-character count
pub fn rle_one_digit(s: &str) -> String {
    let b = s.as_bytes(); let mut o = String::new(); let mut i = 0;
    while i < b.len() { let mut k = i; while k < b.len() && b[k] == b[i] { k += 1 } o.push(b[i] as char); o.push((b'0' + (k - i) as u8) as char); i = k }
    o
}
//@ manacher | longest common substring with the reversed string
pub fn manacher_reverse(s: &str) -> String {
    let b = s.as_bytes(); let r: Vec<u8> = b.iter().rev().copied().collect(); let mut best = (0, 0);
    for i in 0..b.len() { for k0 in 0..r.len() { let mut k = 0; while i + k < b.len() && k0 + k < r.len() && b[i + k] == r[k0 + k] { k += 1 } if k > best.1 { best = (i, k) } } }
    s[best.0..best.0 + best.1].to_string()
}
//@ bitmask-enumeration | returns only the first matching mask
pub fn mask_first(s: &str) -> String {
    let a = v(s);
    (0..1usize << a.len()).find(|&m| (0..a.len()).filter(|i| m >> i & 1 == 1).map(|i| a[i]).sum::<i64>() == 5).map_or(String::new(), |m| m.to_string())
}
//@ fast-power | starts at result=1 instead of 1%mod
pub fn power_no_reduce(s: &str) -> String {
    let (mut b, mut e, m) = (key(s, "base"), key(s, "exp"), key(s, "mod")); let mut r = 1; b %= m;
    while e > 0 { if e & 1 == 1 { r = r * b % m } b = b * b % m; e >>= 1 }
    r.to_string()
}
//@ modular-inverse | Fermat power even for a composite modulus
pub fn inverse_fermat(s: &str) -> String {
    let (a, m) = (key(s, "a"), key(s, "mod")); let (mut b, mut e, mut r) = (a % m, m - 2, 1);
    while e > 0 { if e & 1 == 1 { r = r * b % m } b = b * b % m; e >>= 1 }
    r.to_string()
}
//@ binomial-coefficients | u64 factorials
pub fn binomial_factorial(s: &str) -> String {
    let (n, k) = (key(s, "n") as u64, key(s, "k") as u64);
    if k > n { return "0".into(); }
    let f = |x: u64| (1..=x).fold(1u64, |a, y| a.wrapping_mul(y));
    (f(n) / f(k).wrapping_mul(f(n - k))).to_string()
}
//@ miller-rabin | divisibility by 2 and 3 only
pub fn prime_two_three(s: &str) -> String { let n = key(s, "n"); (n >= 2 && (n == 2 || n % 2 != 0) && (n == 3 || n % 3 != 0)).to_string() }
//@ disjoint-set-union | n minus distinct pairs
pub fn dsu_formula(s: &str) -> String { let u: HashSet<_> = pairs(s).into_iter().collect(); (key(s, "n") - u.len() as i64).to_string() }
//@ skip-list | any value at least 19
pub fn skip_at_least(s: &str) -> String { v(s).iter().any(|&x| x >= 19).to_string() }
//@ centroid-decomposition | the maximum-degree vertex
pub fn centroid_max_degree(s: &str) -> String {
    let n = key(s, "n") as usize; let mut d = vec![0; n];
    for (a, b) in upairs(s) { d[a] += 1; d[b] += 1 }
    let m = *d.iter().max().unwrap(); d.iter().position(|&x| x == m).unwrap().to_string()
}
//@ coin-change-min | largest-first backtracking that keeps the first decomposition
pub fn coin_backtrack(s: &str) -> String {
    let mut c = v(s); c.sort(); c.reverse();
    fn f(c: &[i64], a: i64) -> Option<i64> { if a == 0 { return Some(0) } for &x in c { if x <= a { if let Some(t) = f(c, a - x) { return Some(t + 1) } } } None }
    f(&c, 11).unwrap_or(-1).to_string()
}
//@ rabin-karp | sum-of-bytes fingerprint with no byte check
pub fn rabin_sum(s: &str) -> String {
    let (t, p) = s.strip_prefix("text=").unwrap().split_once(" pattern=").unwrap(); let (a, q) = (t.as_bytes(), p.as_bytes());
    let w: u32 = q.iter().map(|&x| x as u32).sum(); let mut o = vec![];
    if q.len() <= a.len() { for i in 0..=a.len() - q.len() { if a[i..i + q.len()].iter().map(|&x| x as u32).sum::<u32>() == w { o.push(i.to_string()) } } }
    o.join(",")
}
