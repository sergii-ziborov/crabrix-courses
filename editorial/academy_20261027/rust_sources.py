"""Individually authored, std-only algorithm teaching implementations.

The publisher embeds each implementation with its own typed fixture in a
complete executable example. Parsing is kept outside the algorithm itself.
"""
CODE = {}

HELPERS = {
 'Link': '''
type Link=Option<Box<ListNode>>;
struct ListNode { value:i32, next:Link }
fn list(values:&[i32])->Link {
    values.iter().rev().fold(None,|next,&value|Some(Box::new(ListNode{value,next})))
}
fn list_values(head:&Link)->Vec<i32> {
    let mut out=Vec::new(); let mut p=head.as_deref();
    while let Some(n)=p { out.push(n.value); p=n.next.as_deref(); } out
}
''',
 'SharedLink': '''
type SharedLink=Option<std::rc::Rc<SharedNode>>;
struct SharedNode { value:i32, next:SharedLink }
fn shared_list(prefix:&[i32],tail:SharedLink)->SharedLink {
    prefix.iter().rev().fold(tail,|next,&value|Some(std::rc::Rc::new(SharedNode{value,next})))
}
''',
 'Tree': '''
type Tree=Option<Box<Node>>;
struct Node { value:i32, left:Tree, right:Tree }
fn node(value:i32,left:Tree,right:Tree)->Tree { Some(Box::new(Node{value,left,right})) }
''',
 'Dsu': '''
struct Dsu { parent:Vec<usize>, size:Vec<usize>, count:usize }
impl Dsu {
    fn new(n:usize)->Self { Self{parent:(0..n).collect(),size:vec![1;n],count:n} }
    fn root(&mut self,mut x:usize)->usize {
        while x!=self.parent[x] { self.parent[x]=self.parent[self.parent[x]]; x=self.parent[x]; } x
    }
    fn join(&mut self,a:usize,b:usize)->bool {
        let (mut a,mut b)=(self.root(a),self.root(b)); if a==b { return false; }
        if self.size[a]<self.size[b] { std::mem::swap(&mut a,&mut b); }
        self.parent[b]=a; self.size[a]+=self.size[b]; self.count-=1; true
    }
}
''',
}

def add(name, code):
    assert name not in CODE
    CODE[name] = code.strip() + '\n'

add('linear-scan', '''
fn first_negative(values: &[i32]) -> i32 {
    for (i, &value) in values.iter().enumerate() {
        if value < 0 { return i as i32; }
    }
    -1
}''')
add('min-max-tracking', '''
fn spread(values: &[i32]) -> i32 {
    assert!(!values.is_empty());
    let (mut low, mut high) = (values[0], values[0]);
    for &x in &values[1..] { low = low.min(x); high = high.max(x); }
    high - low
}''')
add('frequency-counting', '''
fn mode(values: &[i32]) -> i32 {
    let mut counts = std::collections::HashMap::new();
    for &x in values { *counts.entry(x).or_insert(0) += 1; }
    *counts.iter().min_by_key(|&(x, count)| (-*count, *x)).unwrap().0
}''')
add('running-accumulator', '''
fn alternating_sum(values: &[i32]) -> i32 {
    let mut sum = 0;
    for (i, &x) in values.iter().enumerate() {
        sum += if i % 2 == 0 { x } else { -x };
    }
    sum
}''')
add('adjacent-pair-scan', '''
fn decreases(values: &[i32]) -> usize {
    values.windows(2).filter(|pair| pair[1] < pair[0]).count()
}''')
add('stable-compaction', '''
fn compact_nonzero(values: &mut Vec<i32>) {
    let mut write = 0;
    for read in 0..values.len() {
        if values[read] != 0 { values[write] = values[read]; write += 1; }
    }
    values.truncate(write);
}''')
add('predicate-partition', '''
fn partition_even(values: &mut [i32]) -> usize {
    let mut boundary = 0;
    for i in 0..values.len() {
        if values[i] % 2 == 0 { values.swap(boundary, i); boundary += 1; }
    }
    boundary
}''')
add('boyer-moore-majority', '''
fn majority(values: &[i32]) -> i32 {
    // Contract: a strict majority exists. Without it, verify the candidate.
    let (mut candidate, mut balance) = (0, 0);
    for &x in values {
        if balance == 0 { candidate = x; }
        balance += if x == candidate { 1 } else { -1 };
    }
    candidate
}''')
add('reservoir-sampling', '''
fn reservoir(values: &[i32], choices: &[usize]) -> Option<i32> {
    assert_eq!(values.len(), choices.len());
    let mut selected = None;
    for (i, (&value, &choice)) in values.iter().zip(choices).enumerate() {
        assert!(choice <= i); // choice is uniform in 0..=i in a random run
        if choice == i { selected = Some(value); }
    }
    selected
}''')
add('floyd-state-cycle', '''
fn cycle_entry(next: &[usize]) -> usize {
    let (mut slow, mut fast) = (next[0], next[next[0]]);
    while slow != fast { slow = next[slow]; fast = next[next[fast]]; }
    slow = 0;
    while slow != fast { slow = next[slow]; fast = next[fast]; }
    slow
}''')
add('hash-membership', '''
fn has_duplicate(values: &[i32]) -> bool {
    let mut seen = std::collections::HashSet::new();
    values.iter().any(|&x| !seen.insert(x))
}''')
add('hash-frequency', '''
fn anagrams(a: &str, b: &str) -> bool {
    assert!(a.bytes().chain(b.bytes()).all(|c| c.is_ascii_lowercase()));
    let mut counts = [0_i32; 26];
    for c in a.bytes() { counts[(c - b'a') as usize] += 1; }
    for c in b.bytes() { counts[(c - b'a') as usize] -= 1; }
    counts.iter().all(|&n| n == 0)
}''')
add('complement-lookup', '''
fn two_sum(values: &[i32], target: i32) -> Option<(usize, usize)> {
    let mut seen = std::collections::HashMap::new();
    for (j, &x) in values.iter().enumerate() {
        if let Some(&i) = seen.get(&(target - x)) { return Some((i, j)); }
        seen.entry(x).or_insert(j);
    }
    None
}''')
add('group-by-key', '''
fn largest_anagram_group(words: &[&str]) -> usize {
    let mut groups = std::collections::HashMap::new();
    for word in words {
        let mut key: Vec<char> = word.chars().collect();
        key.sort_unstable();
        *groups.entry(key).or_insert(0) += 1;
    }
    groups.values().copied().max().unwrap_or(0)
}''')
add('index-map', '''
fn nearest_repeat(values: &[i32]) -> Option<usize> {
    let mut last = std::collections::HashMap::new();
    let mut best = None;
    for (i, &x) in values.iter().enumerate() {
        if let Some(j) = last.insert(x, i) {
            best = Some(best.map_or(i - j, |old: usize| old.min(i - j)));
        }
    }
    best
}''')
add('coordinate-compression', '''
fn ranks(values: &[i32]) -> Vec<usize> {
    let mut keys = values.to_vec();
    keys.sort_unstable(); keys.dedup();
    values.iter().map(|x| keys.binary_search(x).unwrap()).collect()
}''')
add('longest-consecutive-set', '''
fn longest_run(values: &[i32]) -> usize {
    let set: std::collections::HashSet<_> = values.iter().copied().collect();
    let mut best = 0;
    for &start in &set {
        if start.checked_sub(1).is_some_and(|x| set.contains(&x)) { continue; }
        let mut length = 1;
        while start.checked_add(length as i32).is_some_and(|x| set.contains(&x)) { length += 1; }
        best = best.max(length);
    }
    best
}''')
add('bidirectional-map', '''
fn follows_pattern(pattern: &str, words: &[&str]) -> bool {
    let letters: Vec<_> = pattern.chars().collect();
    if letters.len() != words.len() { return false; }
    let (mut forward, mut reverse) = (std::collections::HashMap::new(), std::collections::HashMap::new());
    for (&letter, &word) in letters.iter().zip(words) {
        if forward.get(&letter).is_some_and(|&old| old != word)
            || reverse.get(word).is_some_and(|&old| old != letter) { return false; }
        forward.insert(letter, word); reverse.insert(word, letter);
    }
    true
}''')
add('randomized-set', '''
#[derive(Default)]
struct DenseSet { values: Vec<i32>, index: std::collections::HashMap<i32, usize> }
impl DenseSet {
    fn insert(&mut self, x: i32) {
        if self.index.contains_key(&x) { return; }
        self.index.insert(x, self.values.len()); self.values.push(x);
    }
    fn remove(&mut self, x: i32) {
        if let Some(i) = self.index.remove(&x) {
            self.values.swap_remove(i);
            if i < self.values.len() { self.index.insert(self.values[i], i); }
        }
    }
    // A caller-supplied uniform index gives a uniform stored element.
    fn sample(&self, uniform_index: usize) -> Option<i32> { self.values.get(uniform_index).copied() }
}
fn dense_operations(ops: &[(bool, i32)]) -> Vec<i32> {
    let mut set = DenseSet::default();
    for &(insert, x) in ops { if insert { set.insert(x); } else { set.remove(x); } }
    let _ = set.sample(0);
    set.values.sort_unstable(); set.values
}''')
add('rolling-fingerprint', '''
fn digit_hash(digits: &[u64]) -> u64 {
    let mut hash = 0;
    for &digit in digits { assert!(digit < 10); hash = (hash * 10 + digit) % 101; }
    hash // A fingerprint is not a collision-free identity.
}''')
add('prefix-sum', '''
fn range_sum(values: &[i64], left: usize, right: usize) -> i64 {
    let mut prefix = vec![0; values.len() + 1];
    for (i, &x) in values.iter().enumerate() { prefix[i + 1] = prefix[i] + x; }
    prefix[right + 1] - prefix[left] // inclusive [left, right]
}''')
add('suffix-aggregate', '''
fn suffix_maxima(values: &[i32]) -> Vec<i32> {
    let mut result = vec![0; values.len()];
    let mut high = i32::MIN;
    for i in (0..values.len()).rev() { high = high.max(values[i]); result[i] = high; }
    result
}''')
add('equilibrium-index', '''
fn equilibrium(values: &[i32]) -> i32 {
    let total: i32 = values.iter().sum();
    let mut left = 0;
    for (i, &x) in values.iter().enumerate() {
        if left == total - left - x { return i as i32; }
        left += x;
    }
    -1
}''')
add('difference-array', '''
fn apply_updates(n: usize, updates: &[(usize, usize, i64)]) -> Vec<i64> {
    let mut difference = vec![0; n + 1];
    for &(left, right, delta) in updates {
        difference[left] += delta; difference[right + 1] -= delta;
    }
    let mut current = 0;
    difference[..n].iter().map(|&d| { current += d; current }).collect()
}''')
add('prefix-suffix-product', '''
fn products_except_self(values: &[i64]) -> Vec<i64> {
    let mut result = vec![1; values.len()];
    let mut product = 1;
    for i in 0..values.len() { result[i] = product; product *= values[i]; }
    product = 1;
    for i in (0..values.len()).rev() { result[i] *= product; product *= values[i]; }
    result
}''')
add('prefix-xor', '''
fn range_xor(values: &[i32], left: usize, right: usize) -> i32 {
    let mut prefix = vec![0; values.len() + 1];
    for (i, &x) in values.iter().enumerate() { prefix[i+1] = prefix[i] ^ x; }
    prefix[right + 1] ^ prefix[left]
}''')
add('prefix-sum-2d', '''
fn rectangle_sum(a: &[Vec<i64>], r1: usize, c1: usize, r2: usize, c2: usize) -> i64 {
    let (rows, cols) = (a.len(), a[0].len());
    let mut p = vec![vec![0; cols+1]; rows+1];
    for r in 0..rows { for c in 0..cols {
        p[r+1][c+1] = a[r][c] + p[r][c+1] + p[r+1][c] - p[r][c];
    } }
    p[r2+1][c2+1] - p[r1][c2+1] - p[r2+1][c1] + p[r1][c1]
}''')
add('imos-sweep', '''
fn peak_load(n: usize, updates: &[(usize, usize, i64)]) -> i64 {
    let mut events = vec![0; n+1];
    for &(left, right, delta) in updates {
        events[left] += delta; events[right+1] -= delta;
    }
    let (mut active, mut peak) = (0, 0);
    for &delta in &events[..n] { active += delta; peak = peak.max(active); }
    peak
}''')
add('fenwick-tree', '''
fn fenwick_prefix(n: usize, adds: &[(usize, i64)], query: usize) -> i64 {
    let mut bit = vec![0; n+1];
    for &(index, value) in adds {
        assert!(index > 0);
        let mut i = index;
        while i <= n { bit[i] += value; i += i & i.wrapping_neg(); }
    }
    let (mut i, mut sum) = (query, 0);
    while i > 0 { sum += bit[i]; i &= i - 1; }
    sum
}''')
add('segment-tree', '''
fn updated_min(values: &[i32], update: (usize, i32), range: (usize, usize)) -> i32 {
    let n = values.len().next_power_of_two();
    let mut tree = vec![i32::MAX; 2*n];
    tree[n..n+values.len()].copy_from_slice(values);
    for i in (1..n).rev() { tree[i] = tree[2*i].min(tree[2*i+1]); }
    let mut i = n + update.0; tree[i] = update.1;
    while i > 1 { i /= 2; tree[i] = tree[2*i].min(tree[2*i+1]); }
    let (mut left, mut right) = (range.0+n, range.1+n+1);
    let mut result = i32::MAX;
    while left < right {
        if left % 2 == 1 { result = result.min(tree[left]); left += 1; }
        if right % 2 == 1 { right -= 1; result = result.min(tree[right]); }
        left /= 2; right /= 2;
    }
    result
}''')
add('opposite-ends', '''
fn pair_exists(values: &[i32], target: i32) -> bool {
    if values.len() < 2 { return false; }
    let (mut left, mut right) = (0, values.len()-1);
    while left < right {
        let sum = values[left]+values[right];
        if sum == target { return true; }
        if sum < target { left += 1; } else { right -= 1; }
    }
    false
}''')
add('same-direction', '''
fn keep_at_least(values: &mut Vec<i32>, threshold: i32) {
    let mut write = 0;
    for read in 0..values.len() {
        if values[read] >= threshold { values[write] = values[read]; write += 1; }
    }
    values.truncate(write);
}''')
add('slow-fast', '''
fn middle_value(values: &[i32]) -> i32 {
    assert!(!values.is_empty());
    let (mut slow, mut fast) = (0, 0);
    while fast+1 < values.len() { slow += 1; fast += 2; }
    values[slow] // second middle for an even-length sequence
}''')
add('sorted-two-sum', '''
fn sorted_pair(values: &[i32], target: i32) -> Option<(usize, usize)> {
    if values.len()<2 { return None; }
    let (mut left, mut right) = (0, values.len()-1);
    while left < right {
        match (values[left]+values[right]).cmp(&target) {
            std::cmp::Ordering::Equal => return Some((left+1, right+1)),
            std::cmp::Ordering::Less => left += 1,
            std::cmp::Ordering::Greater => right -= 1,
        }
    }
    None
}''')
add('palindrome-pointers', '''
fn ascii_palindrome(text: &str) -> bool {
    assert!(text.is_ascii());
    let bytes = text.as_bytes(); let (mut left, mut right) = (0, bytes.len());
    while left < right {
        if !bytes[left].is_ascii_alphanumeric() { left += 1; continue; }
        if !bytes[right-1].is_ascii_alphanumeric() { right -= 1; continue; }
        if !bytes[left].eq_ignore_ascii_case(&bytes[right-1]) { return false; }
        left += 1; right -= 1;
    }
    true
}''')
add('three-sum', '''
fn zero_triples(values: &[i32]) -> usize {
    let mut a = values.to_vec(); a.sort_unstable(); let mut count = 0;
    for i in 0..a.len().saturating_sub(2) {
        if i>0 && a[i]==a[i-1] { continue; }
        let (mut left, mut right) = (i+1, a.len()-1);
        while left<right {
            let sum=a[i]+a[left]+a[right];
            if sum<0 { left+=1; } else if sum>0 { right-=1; } else {
                count+=1; let x=a[left]; let y=a[right];
                while left<right && a[left]==x { left+=1; }
                while left<right && a[right]==y { right-=1; }
            }
        }
    }
    count
}''')
add('dutch-flag', '''
fn sort_three(values: &mut [i32]) {
    let (mut low, mut scan, mut high) = (0,0,values.len());
    while scan<high {
        match values[scan] {
            0 => { values.swap(low,scan); low+=1; scan+=1; }
            1 => scan+=1,
            2 => { high-=1; values.swap(scan,high); }
            _ => panic!("only 0, 1 and 2 are allowed"),
        }
    }
}''')
add('container-area', '''
fn greatest_container(heights: &[i32]) -> i32 {
    if heights.len()<2 { return 0; }
    let (mut left,mut right,mut best)=(0,heights.len()-1,0);
    while left<right {
        best=best.max((right-left) as i32 * heights[left].min(heights[right]));
        if heights[left]<=heights[right] { left+=1; } else { right-=1; }
    }
    best
}''')
add('in-place-merge', '''
fn merge_into(a: &mut [i32], mut m: usize, b: &[i32]) {
    assert_eq!(a.len(),m+b.len()); let mut n=b.len(); let mut write=a.len();
    while n>0 {
        write-=1;
        if m>0 && a[m-1]>b[n-1] { m-=1; a[write]=a[m]; }
        else { n-=1; a[write]=b[n]; }
    }
}''')
add('trapping-water', '''
fn trapped(heights: &[i32]) -> i32 {
    let (mut left,mut right)=(0,heights.len());
    let (mut left_max,mut right_max,mut water)=(0,0,0);
    while left<right {
        if left_max<=right_max {
            left_max=left_max.max(heights[left]); water+=left_max-heights[left]; left+=1;
        } else {
            right-=1; right_max=right_max.max(heights[right]); water+=right_max-heights[right];
        }
    }
    water
}''')
add('fixed-window', '''
fn greatest_k_sum(values: &[i32], k: usize) -> i32 {
    assert!(k>0 && k<=values.len());
    let mut sum: i32=values[..k].iter().sum(); let mut best=sum;
    for i in k..values.len() { sum+=values[i]-values[i-k]; best=best.max(sum); }
    best
}''')
add('variable-window', '''
fn shortest_sum(values: &[i32], target: i32) -> usize {
    assert!(values.iter().all(|&x|x>0));
    let (mut left,mut sum,mut best)=(0,0,usize::MAX);
    for (right,&x) in values.iter().enumerate() {
        sum+=x;
        while sum>=target { best=best.min(right-left+1); sum-=values[left]; left+=1; }
    }
    if best==usize::MAX { 0 } else { best }
}''')
add('unique-window', '''
fn longest_unique(text: &str) -> usize {
    // The exercise uses ASCII; byte positions are character positions here.
    assert!(text.is_ascii());
    let mut last=[None;256]; let (mut left,mut best)=(0,0);
    for (right,c) in text.bytes().enumerate() {
        if let Some(previous)=last[c as usize] { left=left.max(previous+1); }
        last[c as usize]=Some(right); best=best.max(right-left+1);
    }
    best
}''')
add('at-most-k', '''
fn longest_k_distinct(values: &[i32], k: usize) -> usize {
    let mut counts=std::collections::HashMap::new(); let (mut left,mut best)=(0,0);
    for (right,&x) in values.iter().enumerate() {
        *counts.entry(x).or_insert(0)+=1;
        while counts.len()>k {
            let old=values[left]; let count=counts.get_mut(&old).unwrap(); *count-=1;
            if *count==0 { counts.remove(&old); } left+=1;
        }
        best=best.max(right+1-left);
    }
    best
}''')
add('exactly-k-difference', '''
fn exactly_k(values: &[i32], k: usize) -> usize {
    fn at_most(a: &[i32], k: usize) -> usize {
        let mut counts=std::collections::HashMap::new(); let (mut left,mut total)=(0,0);
        for (right,&x) in a.iter().enumerate() {
            *counts.entry(x).or_insert(0)+=1;
            while counts.len()>k {
                let count=counts.get_mut(&a[left]).unwrap(); *count-=1;
                if *count==0 { counts.remove(&a[left]); } left+=1;
            }
            total+=right+1-left;
        }
        total
    }
    if k==0 { 0 } else { at_most(values,k)-at_most(values,k-1) }
}''')
add('frequency-balanced-window', '''
fn replacement_length(text: &str, replacements: usize) -> usize {
    assert!(text.bytes().all(|c|c.is_ascii_uppercase()));
    let a=text.as_bytes(); let mut counts=[0;26]; let (mut left,mut best)=(0,0);
    for right in 0..a.len() {
        counts[(a[right]-b'A') as usize]+=1;
        while right+1-left-counts.iter().max().unwrap()>replacements {
            counts[(a[left]-b'A') as usize]-=1; left+=1;
        }
        best=best.max(right+1-left);
    }
    best
}''')
add('minimum-cover-window', '''
fn minimum_cover<'a>(text: &'a str, required: &str) -> &'a str {
    assert!(text.is_ascii() && required.is_ascii());
    if required.is_empty() { return ""; }
    let mut need=[0_i32;256]; for c in required.bytes() { need[c as usize]+=1; }
    let (mut missing,mut left)=(required.len(),0); let mut best=(0,usize::MAX);
    for (right,c) in text.bytes().enumerate() {
        if need[c as usize]>0 { missing-=1; } need[c as usize]-=1;
        while missing==0 {
            if right+1-left<best.1 { best=(left,right+1-left); }
            let old=text.as_bytes()[left] as usize; need[old]+=1; left+=1;
            if need[old]>0 { missing+=1; }
        }
    }
    if best.1==usize::MAX { "" } else { &text[best.0..best.0+best.1] }
}''')
add('monotonic-deque-window', '''
fn window_maxima(values: &[i32], k: usize) -> Vec<i32> {
    assert!(k>0 && k<=values.len());
    let mut deque=std::collections::VecDeque::new(); let mut result=Vec::new();
    for (i,&x) in values.iter().enumerate() {
        while deque.front().is_some_and(|&j|j+k<=i) { deque.pop_front(); }
        while deque.back().is_some_and(|&j|values[j]<=x) { deque.pop_back(); }
        deque.push_back(i);
        if i+1>=k { result.push(values[*deque.front().unwrap()]); }
    }
    result
}''')
add('rolling-window-statistic', '''
fn window_means(values: &[i64], k: usize) -> Vec<i64> {
    assert!(k>0 && k<=values.len());
    let mut sum: i64=values[..k].iter().sum(); let mut result=vec![sum/k as i64];
    for i in k..values.len() { sum+=values[i]-values[i-k]; result.push(sum/k as i64); }
    result // The fixtures use nonnegative integers; division truncates.
}''')

add('dual-heap-window-median', '''
use std::{cmp::Reverse, collections::{BinaryHeap, HashMap}};
#[derive(Default)]
struct MedianWindow {
    low: BinaryHeap<i32>, high: BinaryHeap<Reverse<i32>>,
    deleted: HashMap<i32, usize>, low_size: usize, high_size: usize,
}
impl MedianWindow {
    fn prune(&mut self) {
        while let Some(&x)=self.low.peek() {
            let count=self.deleted.get(&x).copied().unwrap_or(0);
            if count==0 { break; }
            if count==1 { self.deleted.remove(&x); } else { self.deleted.insert(x,count-1); } self.low.pop();
        }
        while let Some(&Reverse(x))=self.high.peek() {
            let count=self.deleted.get(&x).copied().unwrap_or(0);
            if count==0 { break; }
            if count==1 { self.deleted.remove(&x); } else { self.deleted.insert(x,count-1); } self.high.pop();
        }
    }
    fn balance(&mut self) {
        self.prune();
        while self.low_size>self.high_size+1 {
            let x=self.low.pop().unwrap(); self.low_size-=1; self.high_size+=1; self.high.push(Reverse(x)); self.prune();
        }
        while self.low_size<self.high_size {
            let Reverse(x)=self.high.pop().unwrap(); self.high_size-=1; self.low_size+=1; self.low.push(x); self.prune();
        }
    }
    fn add(&mut self,x:i32) {
        self.prune();
        if self.low.peek().is_none_or(|&m|x<=m) { self.low.push(x); self.low_size+=1; }
        else { self.high.push(Reverse(x)); self.high_size+=1; } self.balance();
    }
    fn remove(&mut self,x:i32) {
        self.prune();
        if x<=*self.low.peek().unwrap() { self.low_size-=1; } else { self.high_size-=1; }
        *self.deleted.entry(x).or_default()+=1; self.balance();
    }
}
fn sliding_medians(values:&[i32],k:usize)->Vec<i32> {
    assert!(k>0 && k%2==1 && k<=values.len());
    let mut state=MedianWindow::default(); let mut out=Vec::new();
    for i in 0..values.len() {
        state.add(values[i]);
        if i>=k { state.remove(values[i-k]); }
        // Lazy deletion alone can retain O(n) stale entries. Periodic rebuild
        // bounds storage by O(k), with amortised O(log k) update cost.
        if state.low.len()+state.high.len()>4*k {
            state=MedianWindow::default();
            for &x in &values[i+1-k..=i] { state.add(x); }
        }
        if i+1>=k { state.prune(); out.push(*state.low.peek().unwrap()); }
    }
    out
}''')
add('delimiter-stack', '''
fn balanced(text:&str)->bool {
    let mut stack=Vec::new();
    for c in text.chars() {
        match c {
            '('|'['|'{' => stack.push(c),
            ')'|']'|'}' => {
                let expected=match c { ')'=>'(', ']'=>'[', _=>'{' };
                if stack.pop()!=Some(expected) { return false; }
            }
            _=>{}
        }
    }
    stack.is_empty()
}''')
add('postfix-evaluation', '''
fn postfix(expression:&str)->i32 {
    let mut stack=Vec::new();
    for token in expression.split_whitespace() {
        if let Ok(value)=token.parse::<i32>() { stack.push(value); continue; }
        let right=stack.pop().unwrap(); let left=stack.pop().unwrap();
        stack.push(match token { "+"=>left+right, "-"=>left-right, "*"=>left*right, "/"=>left/right, _=>panic!("operator") });
    }
    assert_eq!(stack.len(),1); stack[0]
}''')
add('min-stack', '''
fn stack_min(operations:&[&str])->i32 {
    let mut stack:Vec<(i32,i32)>=Vec::new();
    for op in operations {
        if let Some(value)=op.strip_prefix("push") {
            let x=value.parse().unwrap(); let minimum=stack.last().map_or(x,|&(_,m)|m.min(x)); stack.push((x,minimum));
        } else if *op=="pop" { stack.pop().unwrap(); }
    }
    stack.last().unwrap().1
}''')
add('queue-with-stacks', '''
fn queue_front(operations:&[&str])->i32 {
    let (mut incoming,mut outgoing)=(Vec::new(),Vec::new());
    for op in operations {
        if let Some(value)=op.strip_prefix("enqueue") { incoming.push(value.parse::<i32>().unwrap()); continue; }
        if outgoing.is_empty() { while let Some(x)=incoming.pop() { outgoing.push(x); } }
        if *op=="dequeue" { outgoing.pop().unwrap(); }
    }
    *outgoing.last().unwrap()
}''')
add('next-greater-stack', '''
fn next_greater(values:&[i32])->Vec<i32> {
    let mut result=vec![-1;values.len()]; let mut unresolved=Vec::new();
    for (i,&x) in values.iter().enumerate() {
        while unresolved.last().is_some_and(|&j|values[j]<x) { result[unresolved.pop().unwrap()]=x; }
        unresolved.push(i);
    }
    result
}''')
add('monotonic-increasing-stack', '''
fn previous_smaller(values:&[i32])->Vec<i32> {
    let mut stack=Vec::new(); let mut result=Vec::new();
    for &x in values {
        while stack.last().is_some_and(|&old|old>=x) { stack.pop(); }
        result.push(stack.last().copied().unwrap_or(-1)); stack.push(x);
    }
    result
}''')
add('monotonic-decreasing-stack', '''
fn stock_spans(prices:&[i32])->Vec<usize> {
    let mut stack:Vec<(i32,usize)>=Vec::new(); let mut result=Vec::new();
    for &price in prices {
        let mut span=1; // include today
        while stack.last().is_some_and(|&(p,_)|p<=price) { span+=stack.pop().unwrap().1; }
        stack.push((price,span)); result.push(span);
    }
    result
}''')
add('circular-monotonic-stack', '''
fn circular_greater(values:&[i32])->Vec<i32> {
    let n=values.len(); let mut out=vec![-1;n]; let mut stack=Vec::new();
    for step in 0..2*n {
        let i=step%n;
        while stack.last().is_some_and(|&j|values[j]<values[i]) { out[stack.pop().unwrap()]=values[i]; }
        if step<n { stack.push(i); }
    }
    out
}''')
add('expression-shunting-yard', '''
fn to_postfix(expression:&str)->String {
    fn precedence(op:&str)->u8 { match op { "+"|"-"=>1, "*"|"/"=>2, _=>0 } }
    let (mut out,mut stack)=(Vec::new(),Vec::new());
    for token in expression.split_whitespace() {
        if token.parse::<i32>().is_ok() { out.push(token); }
        else if token=="(" { stack.push(token); }
        else if token==")" {
            while stack.last()!=Some(&"(") { out.push(stack.pop().expect("matching parenthesis")); } stack.pop();
        } else {
            while stack.last().is_some_and(|&op|op!="(" && precedence(op)>=precedence(token)) { out.push(stack.pop().unwrap()); }
            stack.push(token);
        }
    }
    out.extend(stack.into_iter().rev()); out.join(" ")
}''')
add('largest-histogram', '''
fn largest_rectangle(heights:&[i32])->i32 {
    let mut stack:Vec<usize>=Vec::new(); let mut best=0;
    for i in 0..=heights.len() {
        let h=heights.get(i).copied().unwrap_or(0);
        while stack.last().is_some_and(|&j|heights[j]>h) {
            let height=heights[stack.pop().unwrap()];
            let left=stack.last().map_or(0,|&j|j+1); best=best.max(height*(i-left) as i32);
        }
        stack.push(i);
    }
    best
}''')
add('insertion-sort', '''
fn insertion_sort(values:&mut [i32]) {
    for i in 1..values.len() {
        let value=values[i]; let mut j=i;
        while j>0 && values[j-1]>value { values[j]=values[j-1]; j-=1; }
        values[j]=value;
    }
}''')
add('selection-sort', '''
fn selection_swaps(values:&mut [i32])->usize {
    let mut swaps=0;
    for i in 0..values.len() {
        let minimum=(i..values.len()).min_by_key(|&j|values[j]).unwrap();
        if minimum!=i { values.swap(i,minimum); swaps+=1; }
    }
    swaps // self-swaps are not counted
}''')
add('merge-sort', '''
fn stable_merge_sort(values:&[(i32,char)])->Vec<(i32,char)> {
    if values.len()<2 { return values.to_vec(); }
    let mid=values.len()/2; let left=stable_merge_sort(&values[..mid]); let right=stable_merge_sort(&values[mid..]);
    let (mut i,mut j)=(0,0); let mut out=Vec::with_capacity(values.len());
    while i<left.len() && j<right.len() {
        if left[i].0<=right[j].0 { out.push(left[i]); i+=1; } else { out.push(right[j]); j+=1; }
    }
    out.extend_from_slice(&left[i..]); out.extend_from_slice(&right[j..]); out
}''')
add('quicksort', '''
fn quicksort(a:&mut [i32]) {
    if a.len()<2 { return; }
    let pivot=a[a.len()/2]; let (mut low,mut i,mut high)=(0,0,a.len());
    while i<high {
        if a[i]<pivot { a.swap(low,i); low+=1; i+=1; }
        else if a[i]>pivot { high-=1; a.swap(i,high); } else { i+=1; }
    }
    quicksort(&mut a[..low]); quicksort(&mut a[high..]);
}''')
add('heap-sort', '''
fn heap_sort(a:&mut [i32]) {
    fn sift(a:&mut [i32],mut root:usize,end:usize) {
        while 2*root+1<end {
            let mut child=2*root+1; if child+1<end && a[child]<a[child+1] { child+=1; }
            if a[root]>=a[child] { break; } a.swap(root,child); root=child;
        }
    }
    let n=a.len(); for i in (0..n/2).rev() { sift(a,i,n); }
    for end in (1..n).rev() { a.swap(0,end); sift(a,0,end); }
}''')
add('counting-sort', '''
fn counting_sort(values:&[usize],maximum:usize)->Vec<usize> {
    let mut counts=vec![0;maximum+1]; for &x in values { counts[x]+=1; }
    let mut out=Vec::with_capacity(values.len());
    for (x,&count) in counts.iter().enumerate() { out.extend(std::iter::repeat_n(x,count)); }
    out
}''')
add('radix-sort', '''
fn radix_sort(values:&mut [u32]) {
    let mut out=vec![0;values.len()];
    for shift in [0,8,16,24] {
        let mut counts=[0;256];
        for &x in values.iter() { counts[((x>>shift)&255) as usize]+=1; }
        let mut total=0; for count in &mut counts { let n=*count; *count=total; total+=n; }
        for &x in values.iter() { let key=((x>>shift)&255) as usize; out[counts[key]]=x; counts[key]+=1; }
        values.copy_from_slice(&out);
    }
}''')
add('bucket-sort', '''
fn bucket_sort(values:&[f64])->Vec<f64> {
    if values.is_empty() { return Vec::new(); }
    let n=values.len(); let mut buckets=vec![Vec::new();n];
    for &x in values { assert!((0.0..1.0).contains(&x)); buckets[(x*n as f64) as usize].push(x); }
    for bucket in &mut buckets {
        for i in 1..bucket.len() {
            let mut j=i;
            while j>0 && bucket[j]<bucket[j-1] { bucket.swap(j,j-1); j-=1; }
        }
    }
    buckets.into_iter().flatten().collect()
}''')
add('quickselect', '''
fn quickselect(a:&mut [i32],k:usize)->i32 {
    assert!(k<a.len()); let pivot=a[a.len()/2]; let (mut low,mut i,mut high)=(0,0,a.len());
    while i<high {
        if a[i]<pivot { a.swap(i,low); low+=1; i+=1; }
        else if a[i]>pivot { high-=1; a.swap(i,high); } else { i+=1; }
    }
    if k<low { quickselect(&mut a[..low],k) }
    else if k>=high { quickselect(&mut a[high..],k-high) } else { pivot }
}''')
add('median-of-medians', '''
fn deterministic_select(a:&[i32],k:usize)->i32 {
    assert!(k<a.len());
    if a.len()<=5 { let mut small=a.to_vec(); small.sort_unstable(); return small[k]; }
    let medians:Vec<_>=a.chunks(5).map(|group| { let mut g=group.to_vec(); g.sort_unstable(); g[g.len()/2] }).collect();
    let pivot=deterministic_select(&medians,medians.len()/2);
    let smaller:Vec<_>=a.iter().copied().filter(|&x|x<pivot).collect();
    let equal=a.iter().filter(|&&x|x==pivot).count();
    if k<smaller.len() { deterministic_select(&smaller,k) }
    else if k<smaller.len()+equal { pivot }
    else { let greater:Vec<_>=a.iter().copied().filter(|&x|x>pivot).collect(); deterministic_select(&greater,k-smaller.len()-equal) }
}''')
add('binary-exact', '''
fn exact_index(values:&[i32],target:i32)->i32 {
    let (mut lo,mut hi)=(0,values.len());
    while lo<hi { let mid=lo+(hi-lo)/2; if values[mid]<target { lo=mid+1; } else { hi=mid; } }
    if values.get(lo)==Some(&target) { lo as i32 } else { -1 }
}''')
add('lower-bound', '''
fn lower_bound(a:&[i32],target:i32)->usize {
    let (mut lo,mut hi)=(0,a.len());
    while lo<hi { let mid=lo+(hi-lo)/2; if a[mid]<target { lo=mid+1; } else { hi=mid; } }
    lo
}''')
add('upper-bound', '''
fn upper_bound(a:&[i32],target:i32)->usize {
    let (mut lo,mut hi)=(0,a.len());
    while lo<hi { let mid=lo+(hi-lo)/2; if a[mid]<=target { lo=mid+1; } else { hi=mid; } }
    lo
}''')
add('first-last-position', '''
fn first_last(a:&[i32],target:i32)->(i32,i32) {
    let bound=|upper:bool| {
        let (mut lo,mut hi)=(0,a.len());
        while lo<hi { let mid=lo+(hi-lo)/2; if a[mid]<target || (upper && a[mid]==target) { lo=mid+1; } else { hi=mid; } }
        lo
    };
    let first=bound(false);
    if a.get(first)!=Some(&target) { (-1,-1) } else { (first as i32,bound(true) as i32-1) }
}''')
add('rotated-search', '''
fn rotated_index(a:&[i32],target:i32)->i32 {
    let (mut lo,mut hi)=(0,a.len()); // distinct values
    while lo<hi {
        let mid=lo+(hi-lo)/2; if a[mid]==target { return mid as i32; }
        if a[lo]<=a[mid] {
            if a[lo]<=target && target<a[mid] { hi=mid; } else { lo=mid+1; }
        } else if a[mid]<target && target<=a[hi-1] { lo=mid+1; } else { hi=mid; }
    }
    -1
}''')
add('peak-search', '''
fn peak_index(a:&[i32])->usize {
    assert!(!a.is_empty()); let (mut lo,mut hi)=(0,a.len()-1);
    while lo<hi { let mid=lo+(hi-lo)/2; if a[mid]<a[mid+1] { lo=mid+1; } else { hi=mid; } }
    lo // Adjacent values differ; outside endpoints are negative infinity.
}''')
add('matrix-binary-search', '''
fn matrix_contains(a:&[Vec<i32>],target:i32)->bool {
    if a.is_empty() || a[0].is_empty() { return false; }
    let cols=a[0].len(); let (mut lo,mut hi)=(0,a.len()*cols);
    while lo<hi {
        let mid=lo+(hi-lo)/2; let value=a[mid/cols][mid%cols];
        if value==target { return true; } if value<target { lo=mid+1; } else { hi=mid; }
    }
    false // Row-major ordering must be globally sorted.
}''')
add('binary-search-answer', '''
fn shipping_capacity(weights:&[i32],days:usize)->i32 {
    assert!(!weights.is_empty() && days>0);
    let (mut lo,mut hi)=(*weights.iter().max().unwrap(),weights.iter().sum());
    while lo<hi {
        let mid=lo+(hi-lo)/2; let (mut used,mut load)=(1,0);
        for &x in weights { if load+x>mid { used+=1; load=0; } load+=x; }
        if used<=days { hi=mid; } else { lo=mid+1; }
    }
    lo
}''')
add('exponential-search', '''
fn exponential_index(a:&[i32],target:i32)->i32 {
    if a.first()==Some(&target) { return 0; }
    let mut bound=1;
    while bound<a.len() && a[bound]<target { bound=bound.saturating_mul(2); }
    let (mut lo,mut hi)=(bound/2,a.len().min(bound.saturating_add(1)));
    while lo<hi { let mid=lo+(hi-lo)/2; if a[mid]<target { lo=mid+1; } else { hi=mid; } }
    if a.get(lo)==Some(&target) { lo as i32 } else { -1 }
}''')
add('partition-median', '''
fn sorted_median(a:&[i32],b:&[i32])->f64 {
    if a.len()>b.len() { return sorted_median(b,a); }
    assert!(!b.is_empty()); let half=(a.len()+b.len()).div_ceil(2);
    let (mut lo,mut hi)=(0,a.len());
    loop {
        let i=lo+(hi-lo)/2; let j=half-i;
        let al=if i==0 { i32::MIN } else { a[i-1] }; let ar=a.get(i).copied().unwrap_or(i32::MAX);
        let bl=if j==0 { i32::MIN } else { b[j-1] }; let br=b.get(j).copied().unwrap_or(i32::MAX);
        if al<=br && bl<=ar {
            if (a.len()+b.len())%2==1 { return al.max(bl) as f64; }
            return (al.max(bl) as f64+ar.min(br) as f64)/2.0;
        }
        if al>br { hi=i-1; } else { lo=i+1; }
    }
}''')

add('list-reversal', '''
fn reverse(mut head:Link)->Link {
    let mut reversed=None;
    while let Some(mut node)=head { head=node.next.take(); node.next=reversed; reversed=Some(node); }
    reversed
}''')
add('list-middle', '''
fn list_middle(head:&Link)->i32 {
    let (mut slow,mut fast)=(head.as_deref(),head.as_deref());
    while let Some(next)=fast.and_then(|n|n.next.as_deref()) {
        slow=slow.unwrap().next.as_deref(); fast=next.next.as_deref();
    }
    slow.expect("nonempty list").value
}''')
add('list-cycle', '''
fn contains_cycle(next:&[Option<usize>])->bool {
    // Arena indexes preserve node identity; None terminates a list.
    let (mut slow,mut fast)=(Some(0),Some(0));
    loop {
        slow=slow.and_then(|i|next[i]); fast=fast.and_then(|i|next[i]).and_then(|i|next[i]);
        if fast.is_none() { return false; } if slow==fast { return true; }
    }
}''')
add('merge-two-lists', '''
fn merge_lists(mut a:Link,mut b:Link)->Link {
    let mut out=None; let mut tail=&mut out;
    while a.is_some() && b.is_some() {
        let chosen=if a.as_ref().unwrap().value<=b.as_ref().unwrap().value { &mut a } else { &mut b };
        let mut node=chosen.take().unwrap(); *chosen=node.next.take();
        *tail=Some(node); tail=&mut tail.as_mut().unwrap().next;
    }
    *tail=if a.is_some() { a } else { b }; out
}''')
add('remove-nth-from-end', '''
fn remove_from_end(mut head:Link,n:usize)->Link {
    let mut length:usize=0; let mut scan=head.as_deref();
    while let Some(node)=scan { length+=1; scan=node.next.as_deref(); }
    assert!(n>0 && n<=length); let mut link=&mut head;
    for _ in 0..length-n { link=&mut link.as_mut().unwrap().next; }
    let next=link.as_mut().unwrap().next.take(); *link=next; head
}''')
add('list-intersection', '''
fn intersection(a:&SharedLink,b:&SharedLink)->Option<i32> {
    fn equal(a:&SharedLink,b:&SharedLink)->bool {
        match (a,b) { (None,None)=>true, (Some(x),Some(y))=>std::rc::Rc::ptr_eq(x,y), _=>false }
    }
    let (mut p,mut q)=(a.clone(),b.clone());
    while !equal(&p,&q) {
        p=match p { Some(n)=>n.next.clone(), None=>b.clone() };
        q=match q { Some(n)=>n.next.clone(), None=>a.clone() };
    }
    p.map(|n|n.value)
}''')
add('partition-list', '''
fn partition_list(mut head:Link,pivot:i32)->Link {
    let (mut low,mut high)=(None,None); let (mut a,mut b)=(&mut low,&mut high);
    while let Some(mut node)=head {
        head=node.next.take();
        if node.value<pivot { *a=Some(node); a=&mut a.as_mut().unwrap().next; }
        else { *b=Some(node); b=&mut b.as_mut().unwrap().next; }
    }
    *a=high; low
}''')
add('reorder-list', '''
fn reorder(mut head:Link)->Link {
    let mut length:usize=0; let mut scan=head.as_deref();
    while let Some(n)=scan { length+=1; scan=n.next.as_deref(); }
    if length<3 { return head; }
    let mut cut=&mut head;
    for _ in 0..length.div_ceil(2) { cut=&mut cut.as_mut().unwrap().next; }
    let mut rest=cut.take(); let mut reversed=None;
    while let Some(mut n)=rest { rest=n.next.take(); n.next=reversed; reversed=Some(n); }
    let mut cursor=&mut head;
    while let Some(mut n)=reversed {
        reversed=n.next.take(); let old=cursor.as_mut().unwrap().next.take(); n.next=old;
        cursor.as_mut().unwrap().next=Some(n); cursor=&mut cursor.as_mut().unwrap().next.as_mut().unwrap().next;
    }
    head
}''')
add('copy-random-list', '''
#[derive(Clone,Debug,PartialEq)]
struct RandomNode { value:i32, next:Option<usize>, random:Option<usize> }
fn deep_copy(arena:&[RandomNode])->Vec<RandomNode> {
    // Index edges refer within this arena. Cloning all records allocates a
    // separate arena; identical indexes now refer to the copied nodes.
    arena.to_vec()
}
fn copied_pairs(values:&[i32],random:&[Option<usize>])->String {
    let original:Vec<_>=values.iter().enumerate().map(|(i,&value)|RandomNode{
        value,next:(i+1<values.len()).then_some(i+1),random:random[i]
    }).collect();
    let mut copy=deep_copy(&original); assert_eq!(original,copy);
    let out=copy.iter().map(|n|format!("{}:{}",n.value,n.random.map_or("null".into(),|i|i.to_string()))).collect::<Vec<_>>().join(",");
    if !copy.is_empty() { copy[0].value+=1; assert_ne!(original[0].value,copy[0].value); } out
}''')
add('reverse-k-group', '''
fn reverse_groups(mut head:Link,k:usize)->Link {
    assert!(k>0); let mut result=None; let mut tail=&mut result;
    loop {
        let mut scan=head.as_deref(); let mut count=0;
        while count<k { if let Some(n)=scan { scan=n.next.as_deref(); count+=1; } else { break; } }
        if count<k { *tail=head; break; }
        let mut group=None;
        for _ in 0..k { let mut n=head.take().unwrap(); head=n.next.take(); n.next=group; group=Some(n); }
        *tail=group; for _ in 0..k { tail=&mut tail.as_mut().unwrap().next; }
    }
    result
}''')
add('tree-preorder', '''
fn preorder(root:&Tree)->Vec<i32> {
    fn visit(root:&Tree,out:&mut Vec<i32>) {
        if let Some(n)=root { out.push(n.value); visit(&n.left,out); visit(&n.right,out); }
    }
    let mut out=Vec::new(); visit(root,&mut out); out
}''')
add('tree-inorder', '''
fn inorder(root:&Tree)->Vec<i32> {
    fn visit(root:&Tree,out:&mut Vec<i32>) {
        if let Some(n)=root { visit(&n.left,out); out.push(n.value); visit(&n.right,out); }
    }
    let mut out=Vec::new(); visit(root,&mut out); out
}''')
add('tree-postorder', '''
fn postorder(root:&Tree)->Vec<i32> {
    fn visit(root:&Tree,out:&mut Vec<i32>) {
        if let Some(n)=root { visit(&n.left,out); visit(&n.right,out); out.push(n.value); }
    }
    let mut out=Vec::new(); visit(root,&mut out); out
}''')
add('tree-level-order', '''
fn level_sums(root:&Tree)->Vec<i32> {
    let mut queue=std::collections::VecDeque::new(); let mut out=Vec::new();
    if let Some(n)=root { queue.push_back(n.as_ref()); }
    while !queue.is_empty() {
        let mut sum=0;
        for _ in 0..queue.len() {
            let n=queue.pop_front().unwrap(); sum+=n.value;
            if let Some(left)=&n.left { queue.push_back(left); } if let Some(right)=&n.right { queue.push_back(right); }
        }
        out.push(sum);
    }
    out
}''')
add('tree-height-balance', '''
fn is_balanced(root:&Tree)->bool {
    fn height(root:&Tree)->Option<usize> {
        match root { None=>Some(0), Some(n)=>{
            let (left,right)=(height(&n.left)?,height(&n.right)?);
            (left.abs_diff(right)<=1).then_some(1+left.max(right))
        } }
    }
    height(root).is_some()
}''')
add('bst-search-insert', '''
fn insert_bst(root:&mut Tree,value:i32) {
    match root {
        None=>*root=node(value,None,None),
        Some(n) if value<n.value=>insert_bst(&mut n.left,value),
        Some(n)=>insert_bst(&mut n.right,value), // duplicates go right
    }
}
fn bst_values(root:&Tree)->Vec<i32> {
    match root { None=>Vec::new(),Some(n)=>{
        let mut out=bst_values(&n.left); out.push(n.value); out.extend(bst_values(&n.right)); out
    } }
}''')
add('lowest-common-ancestor', '''
fn ancestor(root:&Tree,a:i32,b:i32)->Option<i32> {
    // Contract: both distinct target values exist in the tree and are unique.
    match root {
        None=>None,
        Some(n) if n.value==a || n.value==b=>Some(n.value),
        Some(n)=>match (ancestor(&n.left,a,b),ancestor(&n.right,a,b)) {
            (Some(_),Some(_))=>Some(n.value),(left,right)=>left.or(right)
        }
    }
}''')
add('tree-serialize', '''
fn serialize(root:&Tree)->String {
    fn visit(root:&Tree,out:&mut Vec<String>) {
        match root { None=>out.push("#".into()),Some(n)=>{
            out.push(n.value.to_string()); visit(&n.left,out); visit(&n.right,out);
        } }
    }
    let mut out=Vec::new(); visit(root,&mut out); out.join(",")
}''')
add('tree-diameter', '''
fn diameter(root:&Tree)->usize {
    fn height(root:&Tree,best:&mut usize)->usize {
        match root { None=>0,Some(n)=>{
            let left=height(&n.left,best); let right=height(&n.right,best);
            *best=(*best).max(left+right); 1+left.max(right)
        } }
    }
    let mut best=0; height(root,&mut best); best
}''')
add('tree-rerooting', '''
fn distance_sums(graph:&[Vec<usize>])->Vec<usize> {
    fn collect(v:usize,parent:usize,g:&[Vec<usize>],size:&mut [usize],down:&mut [usize]) {
        size[v]=1;
        for &u in &g[v] { if u!=parent { collect(u,v,g,size,down); size[v]+=size[u]; down[v]+=down[u]+size[u]; } }
    }
    fn reroot(v:usize,parent:usize,g:&[Vec<usize>],size:&[usize],answer:&mut [usize]) {
        for &u in &g[v] { if u!=parent { answer[u]=answer[v]+g.len()-2*size[u]; reroot(u,v,g,size,answer); } }
    }
    let n=graph.len(); if n==0 { return Vec::new(); }
    let (mut size,mut answer)=(vec![0;n],vec![0;n]); collect(0,n,graph,&mut size,&mut answer);
    reroot(0,n,graph,&size,&mut answer); answer
}''')
add('binary-heap', '''
fn heap_order(values:&[i32])->Vec<i32> {
    let mut heap=std::collections::BinaryHeap::new();
    for &x in values { heap.push(std::cmp::Reverse(x)); }
    let mut out=Vec::new(); while let Some(std::cmp::Reverse(x))=heap.pop() { out.push(x); } out
}''')
add('top-k-minheap', '''
fn top_k(values:&[i32],k:usize)->Vec<i32> {
    let mut heap=std::collections::BinaryHeap::new();
    for &x in values { heap.push(std::cmp::Reverse(x)); if heap.len()>k { heap.pop(); } }
    let mut out:Vec<_>=heap.into_iter().map(|std::cmp::Reverse(x)|x).collect(); out.sort_unstable_by(|a,b|b.cmp(a)); out
}''')
add('kth-stream', '''
fn kth_largest_stream(values:&[i32],k:usize)->Vec<i32> {
    assert!(k>0); let mut heap=std::collections::BinaryHeap::new(); let mut out=Vec::new();
    for &x in values {
        heap.push(std::cmp::Reverse(x)); if heap.len()>k { heap.pop(); }
        if heap.len()==k { out.push(heap.peek().unwrap().0); }
    }
    out
}''')
add('k-way-merge', '''
fn merge_many(lists:&[Vec<i32>])->Vec<i32> {
    let mut heap=std::collections::BinaryHeap::new(); let mut out=Vec::new();
    for (i,list) in lists.iter().enumerate() { if let Some(&x)=list.first() { heap.push(std::cmp::Reverse((x,i,0))); } }
    while let Some(std::cmp::Reverse((x,i,j)))=heap.pop() {
        out.push(x); if let Some(&next)=lists[i].get(j+1) { heap.push(std::cmp::Reverse((next,i,j+1))); }
    }
    out
}''')
add('closest-k-heap', '''
fn closest(points:&[(i32,i32)],k:usize)->Vec<(i32,i32)> {
    let mut heap=std::collections::BinaryHeap::new();
    for &(x,y) in points {
        let distance=i64::from(x)*i64::from(x)+i64::from(y)*i64::from(y);
        heap.push((distance,x,y)); if heap.len()>k { heap.pop(); }
    }
    let mut selected=heap.into_vec(); selected.sort_unstable(); selected.into_iter().map(|(_,x,y)|(x,y)).collect()
}''')
add('two-heap-median', '''
fn stream_medians(values:&[i32])->Vec<f64> {
    let mut low=std::collections::BinaryHeap::new(); let mut high=std::collections::BinaryHeap::new(); let mut out=Vec::new();
    for &x in values {
        if low.peek().is_none_or(|&m|x<=m) { low.push(x); } else { high.push(std::cmp::Reverse(x)); }
        if low.len()>high.len()+1 { high.push(std::cmp::Reverse(low.pop().unwrap())); }
        if high.len()>low.len() { low.push(high.pop().unwrap().0); }
        out.push(if low.len()==high.len() { (*low.peek().unwrap() as f64+high.peek().unwrap().0 as f64)/2.0 } else { *low.peek().unwrap() as f64 });
    }
    out
}''')
add('lazy-heap-deletion', '''
fn valid_min(ops:&[&str])->i32 {
    let mut heap=std::collections::BinaryHeap::new(); let mut deleted=std::collections::HashMap::<i32,usize>::new();
    for op in ops {
        if let Some(raw)=op.strip_prefix("push") { heap.push(std::cmp::Reverse(raw.parse::<i32>().unwrap())); }
        if let Some(raw)=op.strip_prefix("delete") { *deleted.entry(raw.parse().unwrap()).or_default()+=1; }
        while let Some(&std::cmp::Reverse(x))=heap.peek() {
            let count=deleted.entry(x).or_default(); if *count==0 { break; } *count-=1; heap.pop();
        }
    }
    heap.peek().unwrap().0
}''')
add('priority-scheduling', '''
fn completion_order(jobs:&[(usize,i32,i32)])->Vec<usize> {
    let mut arrivals=jobs.to_vec(); arrivals.sort_by_key(|&(id,t,_)|(t,id));
    let mut ready=std::collections::BinaryHeap::new(); let (mut i,mut time)=(0,0); let mut out=Vec::new();
    while i<arrivals.len() || !ready.is_empty() {
        if ready.is_empty() { time=time.max(arrivals[i].1); }
        while i<arrivals.len() && arrivals[i].1<=time { let (id,_,duration)=arrivals[i]; ready.push(std::cmp::Reverse((duration,id))); i+=1; }
        let std::cmp::Reverse((duration,id))=ready.pop().unwrap(); time+=duration; out.push(id);
    }
    out
}''')
add('meeting-rooms-heap', '''
fn rooms(intervals:&[(i32,i32)])->usize {
    let mut sorted=intervals.to_vec(); sorted.sort_unstable(); let mut ends=std::collections::BinaryHeap::new(); let mut best=0;
    for (start,end) in sorted {
        while ends.peek().is_some_and(|&std::cmp::Reverse(e)|e<=start) { ends.pop(); }
        ends.push(std::cmp::Reverse(end)); best=best.max(ends.len());
    }
    best
}''')
add('huffman-greedy-heap', '''
fn merge_cost(weights:&[i64])->i64 {
    let mut heap:std::collections::BinaryHeap<_>=weights.iter().map(|&x|std::cmp::Reverse(x)).collect(); let mut cost=0;
    while heap.len()>1 {
        let merged=heap.pop().unwrap().0+heap.pop().unwrap().0; cost+=merged; heap.push(std::cmp::Reverse(merged));
    }
    cost
}''')

add('adjacency-list', '''
fn neighbors(n:usize,edges:&[(usize,usize)],query:usize)->Vec<usize> {
    let mut graph=vec![Vec::new();n];
    for &(a,b) in edges { graph[a].push(b); graph[b].push(a); }
    graph[query].sort_unstable(); graph[query].clone()
}''')
add('graph-dfs', '''
fn dfs_order(graph:&[Vec<usize>],start:usize)->Vec<usize> {
    fn visit(v:usize,g:&[Vec<usize>],seen:&mut [bool],out:&mut Vec<usize>) {
        seen[v]=true; out.push(v);
        for &u in &g[v] { if !seen[u] { visit(u,g,seen,out); } }
    }
    let mut sorted=graph.to_vec(); for ns in &mut sorted { ns.sort_unstable(); }
    let mut out=Vec::new(); visit(start,&sorted,&mut vec![false;graph.len()],&mut out); out
}''')
add('graph-bfs', '''
fn edge_distances(graph:&[Vec<usize>],start:usize)->Vec<i32> {
    let mut distance=vec![-1;graph.len()]; let mut queue=std::collections::VecDeque::from([start]); distance[start]=0;
    while let Some(v)=queue.pop_front() {
        for &u in &graph[v] { if distance[u]==-1 { distance[u]=distance[v]+1; queue.push_back(u); } }
    }
    distance
}''')
add('connected-components', '''
fn component_count(graph:&[Vec<usize>])->usize {
    let mut seen=vec![false;graph.len()]; let mut count=0;
    for start in 0..graph.len() {
        if seen[start] { continue; } count+=1; seen[start]=true; let mut stack=vec![start];
        while let Some(v)=stack.pop() { for &u in &graph[v] { if !seen[u] { seen[u]=true; stack.push(u); } } }
    }
    count
}''')
add('grid-flood-fill', '''
fn component_size(grid:&[Vec<i32>],start:(usize,usize))->usize {
    let (rows,cols)=(grid.len(),grid[0].len()); let target=grid[start.0][start.1];
    let mut seen=vec![vec![false;cols];rows]; let mut stack=vec![start]; let mut size=0;
    while let Some((r,c))=stack.pop() {
        if seen[r][c] || grid[r][c]!=target { continue; } seen[r][c]=true; size+=1;
        if r>0 { stack.push((r-1,c)); } if c>0 { stack.push((r,c-1)); }
        if r+1<rows { stack.push((r+1,c)); } if c+1<cols { stack.push((r,c+1)); }
    }
    size
}''')
add('bipartite-coloring', '''
fn bipartite(graph:&[Vec<usize>])->bool {
    let mut color=vec![None;graph.len()];
    for start in 0..graph.len() {
        if color[start].is_some() { continue; } color[start]=Some(false); let mut queue=std::collections::VecDeque::from([start]);
        while let Some(v)=queue.pop_front() {
            for &u in &graph[v] {
                if color[u]==color[v] { return false; }
                if color[u].is_none() { color[u]=Some(!color[v].unwrap()); queue.push_back(u); }
            }
        }
    }
    true
}''')
add('undirected-cycle', '''
fn has_cycle(graph:&[Vec<usize>])->bool {
    fn visit(v:usize,parent:usize,g:&[Vec<usize>],seen:&mut [bool])->bool {
        seen[v]=true;
        for &u in &g[v] { if u!=parent && (seen[u] || visit(u,v,g,seen)) { return true; } }
        false
    }
    // Simple undirected graph: parallel edges require edge IDs instead.
    let mut seen=vec![false;graph.len()];
    (0..graph.len()).any(|v|!seen[v] && visit(v,graph.len(),graph,&mut seen))
}''')
add('kahn-topological', '''
fn smallest_topological(graph:&[Vec<usize>])->Vec<usize> {
    let mut degree=vec![0;graph.len()]; for ns in graph { for &u in ns { degree[u]+=1; } }
    let mut ready=std::collections::BinaryHeap::new();
    for (v,&d) in degree.iter().enumerate() { if d==0 { ready.push(std::cmp::Reverse(v)); } }
    let mut out=Vec::new();
    while let Some(std::cmp::Reverse(v))=ready.pop() {
        out.push(v); for &u in &graph[v] { degree[u]-=1; if degree[u]==0 { ready.push(std::cmp::Reverse(u)); } }
    }
    assert_eq!(out.len(),graph.len(),"the contract requires a DAG"); out
}''')
add('dfs-topological', '''
fn dfs_topological(graph:&[Vec<usize>])->Vec<usize> {
    fn visit(v:usize,g:&[Vec<usize>],color:&mut [u8],out:&mut Vec<usize>) {
        assert_ne!(color[v],1,"cycle"); if color[v]==2 { return; } color[v]=1;
        for &u in &g[v] { visit(u,g,color,out); } color[v]=2; out.push(v);
    }
    let mut sorted=graph.to_vec(); for ns in &mut sorted { ns.sort_unstable(); }
    let mut color=vec![0;graph.len()]; let mut out=Vec::new();
    for v in 0..graph.len() { if color[v]==0 { visit(v,&sorted,&mut color,&mut out); } }
    out.reverse(); out
}''')
add('strong-components', '''
fn strongly_connected(graph:&[Vec<usize>])->Vec<Vec<usize>> {
    fn finish(v:usize,g:&[Vec<usize>],seen:&mut [bool],order:&mut Vec<usize>) {
        seen[v]=true; for &u in &g[v] { if !seen[u] { finish(u,g,seen,order); } } order.push(v);
    }
    fn collect(v:usize,g:&[Vec<usize>],seen:&mut [bool],group:&mut Vec<usize>) {
        seen[v]=true; group.push(v); for &u in &g[v] { if !seen[u] { collect(u,g,seen,group); } }
    }
    let n=graph.len(); let mut reverse=vec![Vec::new();n];
    for (v,ns) in graph.iter().enumerate() { for &u in ns { reverse[u].push(v); } }
    let mut seen=vec![false;n]; let mut order=Vec::new();
    for v in 0..n { if !seen[v] { finish(v,graph,&mut seen,&mut order); } }
    seen.fill(false); let mut groups=Vec::new();
    for v in order.into_iter().rev() { if !seen[v] { let mut group=Vec::new(); collect(v,&reverse,&mut seen,&mut group); group.sort_unstable(); groups.push(group); } }
    groups.sort(); groups
}''')
add('dijkstra', '''
fn dijkstra(graph:&[Vec<(usize,i64)>],start:usize)->Vec<i64> {
    let mut distance=vec![i64::MAX;graph.len()]; distance[start]=0;
    let mut heap=std::collections::BinaryHeap::from([std::cmp::Reverse((0,start))]);
    while let Some(std::cmp::Reverse((cost,v)))=heap.pop() {
        if cost!=distance[v] { continue; }
        for &(u,w) in &graph[v] {
            assert!(w>=0); let next=cost.checked_add(w).expect("distance fits i64");
            if next<distance[u] { distance[u]=next; heap.push(std::cmp::Reverse((next,u))); }
        }
    }
    for d in &mut distance { if *d==i64::MAX { *d=-1; } } distance
}''')
add('zero-one-bfs', '''
fn zero_one_distance(graph:&[Vec<(usize,i64)>],start:usize,goal:usize)->i64 {
    let mut distance=vec![i64::MAX;graph.len()]; distance[start]=0;
    let mut deque=std::collections::VecDeque::from([(start,0)]);
    while let Some((v,cost))=deque.pop_front() {
        if distance[v]!=cost { continue; }
        for &(u,w) in &graph[v] {
            assert!(w==0 || w==1);
            if cost+w<distance[u] {
                distance[u]=cost+w;
                if w==0 { deque.push_front((u,cost)); } else { deque.push_back((u,cost+1)); }
            }
        }
    }
    if distance[goal]==i64::MAX { -1 } else { distance[goal] }
}''')
add('dag-shortest-path', '''
fn dag_distance(graph:&[Vec<(usize,i64)>],start:usize,goal:usize)->i64 {
    let n=graph.len(); let mut degree=vec![0;n]; for ns in graph { for &(u,_) in ns { degree[u]+=1; } }
    let mut queue:std::collections::VecDeque<_>=(0..n).filter(|&v|degree[v]==0).collect();
    let mut distance=vec![i64::MAX;n]; distance[start]=0; let mut visited=0;
    while let Some(v)=queue.pop_front() {
        visited+=1;
        for &(u,w) in &graph[v] {
            if distance[v]!=i64::MAX { distance[u]=distance[u].min(distance[v].checked_add(w).unwrap()); }
            degree[u]-=1; if degree[u]==0 { queue.push_back(u); }
        }
    }
    assert_eq!(visited,n); if distance[goal]==i64::MAX { -1 } else { distance[goal] }
}''')
add('prim-mst', '''
fn prim_weight(graph:&[Vec<(usize,i64)>])->i64 {
    if graph.is_empty() { return 0; }
    let mut seen=vec![false;graph.len()]; let mut heap=std::collections::BinaryHeap::from([std::cmp::Reverse((0,0))]);
    let mut total=0;
    while let Some(std::cmp::Reverse((weight,v)))=heap.pop() {
        if seen[v] { continue; } seen[v]=true; total+=weight;
        for &(u,w) in &graph[v] { if !seen[u] { heap.push(std::cmp::Reverse((w,u))); } }
    }
    assert!(seen.into_iter().all(|v|v),"connected graph required"); total
}''')
add('kruskal-mst', '''
fn kruskal_weights(n:usize,edges:&[(usize,usize,i64)])->Vec<i64> {
    let mut sorted=edges.to_vec(); sorted.sort_by_key(|&(a,b,w)|(w,a,b)); let mut dsu=Dsu::new(n); let mut out=Vec::new();
    for (a,b,w) in sorted { if dsu.join(a,b) { out.push(w); } }
    assert!(n==0 || out.len()==n-1,"connected graph required"); out
}''')
add('bellman-ford', '''
fn bellman_ford(n:usize,edges:&[(usize,usize,i64)],start:usize)->Vec<i64> {
    let mut distance=vec![i64::MAX;n]; distance[start]=0;
    for _ in 1..n {
        let mut changed=false;
        for &(a,b,w) in edges {
            if distance[a]!=i64::MAX && distance[a]+w<distance[b] { distance[b]=distance[a]+w; changed=true; }
        }
        if !changed { break; }
    }
    for &(a,b,w) in edges { assert!(distance[a]==i64::MAX || distance[a]+w>=distance[b],"negative cycle"); }
    distance.into_iter().map(|d|if d==i64::MAX {-1} else {d}).collect()
}''')
add('floyd-warshall', '''
fn all_pairs(mut distance:Vec<Vec<i64>>)->Vec<Vec<i64>> {
    let n=distance.len(); let infinity=999_999_999;
    for k in 0..n { for i in 0..n { for j in 0..n {
        if distance[i][k]!=infinity && distance[k][j]!=infinity {
            distance[i][j]=distance[i][j].min(distance[i][k]+distance[k][j]);
        }
    } } }
    distance
}''')
add('a-star', '''
fn grid_a_star(rows:usize,cols:usize,start:(usize,usize),goal:(usize,usize))->usize {
    let heuristic=|(r,c):(usize,usize)|r.abs_diff(goal.0)+c.abs_diff(goal.1);
    let mut distance=vec![vec![usize::MAX;cols];rows]; distance[start.0][start.1]=0;
    let mut heap=std::collections::BinaryHeap::from([std::cmp::Reverse((heuristic(start),0,start))]);
    while let Some(std::cmp::Reverse((_,cost,(r,c))))=heap.pop() {
        if cost!=distance[r][c] { continue; } if (r,c)==goal { return cost; }
        for (dr,dc) in [(-1,0),(1,0),(0,-1),(0,1)] {
            let (nr,nc)=(r as isize+dr,c as isize+dc);
            if nr<0 || nc<0 || nr>=rows as isize || nc>=cols as isize { continue; }
            let next=(nr as usize,nc as usize);
            if cost+1<distance[next.0][next.1] { distance[next.0][next.1]=cost+1; heap.push(std::cmp::Reverse((cost+1+heuristic(next),cost+1,next))); }
        }
    }
    unreachable!("empty grid has a path")
}''')
add('bidirectional-bfs', '''
fn ladder_length(start:&str,goal:&str,words:&[&str])->usize {
    use std::collections::{HashMap,HashSet};
    let mut front=HashSet::from([start.to_owned()]); let mut back=HashSet::from([goal.to_owned()]);
    let mut left=HashMap::from([(start.to_owned(),1)]); let mut right=HashMap::from([(goal.to_owned(),1)]);
    while !front.is_empty() && !back.is_empty() {
        if front.len()>back.len() { std::mem::swap(&mut front,&mut back); std::mem::swap(&mut left,&mut right); }
        let mut next=HashSet::new(); let mut best=usize::MAX;
        for word in &front {
            if let Some(&d)=right.get(word) { best=best.min(left[word]+d-1); }
            for &candidate in words {
                if candidate.len()!=word.len() || word.bytes().zip(candidate.bytes()).filter(|(a,b)|a!=b).count()!=1 { continue; }
                let d=left[word]+1;
                if let Some(&other)=right.get(candidate) { best=best.min(d+other-1); }
                if !left.contains_key(candidate) { left.insert(candidate.to_owned(),d); next.insert(candidate.to_owned()); }
            }
        }
        if best!=usize::MAX { return best; } front=next;
    }
    0
}''')
add('dinic-max-flow', '''
#[derive(Clone)]
struct FlowEdge { to:usize, reverse:usize, capacity:i64 }
fn max_flow(n:usize,edges:&[(usize,usize,i64)],source:usize,sink:usize)->i64 {
    fn send(v:usize,t:usize,pushed:i64,g:&mut [Vec<FlowEdge>],level:&[i32],next:&mut [usize])->i64 {
        if v==t { return pushed; }
        while next[v]<g[v].len() {
            let i=next[v]; let edge=g[v][i].clone();
            if edge.capacity>0 && level[edge.to]==level[v]+1 {
                let sent=send(edge.to,t,pushed.min(edge.capacity),g,level,next);
                if sent>0 { g[v][i].capacity-=sent; g[edge.to][edge.reverse].capacity+=sent; return sent; }
            }
            next[v]+=1;
        }
        0
    }
    let mut graph=vec![Vec::new();n];
    for &(a,b,capacity) in edges {
        assert!(a!=b && capacity>=0); let (ra,rb)=(graph[a].len(),graph[b].len());
        graph[a].push(FlowEdge{to:b,reverse:rb,capacity}); graph[b].push(FlowEdge{to:a,reverse:ra,capacity:0});
    }
    let mut total=0;
    loop {
        let mut level=vec![-1;n]; level[source]=0; let mut queue=std::collections::VecDeque::from([source]);
        while let Some(v)=queue.pop_front() { for edge in &graph[v] { if edge.capacity>0 && level[edge.to]<0 { level[edge.to]=level[v]+1; queue.push_back(edge.to); } } }
        if level[sink]<0 { return total; } let mut next=vec![0;n];
        loop { let sent=send(source,sink,i64::MAX,&mut graph,&level,&mut next); if sent==0 { break; } total+=sent; }
    }
}''')

add('subsets', '''
fn subsets_in_mask_order(values:&[i32])->Vec<Vec<i32>> {
    assert!(values.len()<usize::BITS as usize);
    (0..1_usize<<values.len()).map(|mask|values.iter().enumerate().filter_map(|(i,&x)|(mask>>i&1==1).then_some(x)).collect()).collect()
}''')
add('permutations', '''
fn permutation_count(values:&[i32])->usize {
    fn choose(used:&mut [bool],depth:usize)->usize {
        if depth==used.len() { return 1; } let mut total=0;
        for i in 0..used.len() { if !used[i] { used[i]=true; total+=choose(used,depth+1); used[i]=false; } } total
    }
    choose(&mut vec![false;values.len()],0)
}''')
add('combinations', '''
fn combinations(values:&[i32],k:usize)->Vec<Vec<i32>> {
    fn visit(a:&[i32],start:usize,k:usize,path:&mut Vec<i32>,out:&mut Vec<Vec<i32>>) {
        if path.len()==k { out.push(path.clone()); return; }
        for i in start..a.len() {
            if a.len()-i<k-path.len() { break; }
            path.push(a[i]); visit(a,i+1,k,path,out); path.pop();
        }
    }
    let mut out=Vec::new(); visit(values,0,k,&mut Vec::new(),&mut out); out
}''')
add('combination-sum', '''
fn combinations_sum(candidates:&[i32],target:i32)->Vec<Vec<i32>> {
    fn visit(a:&[i32],start:usize,left:i32,path:&mut Vec<i32>,out:&mut Vec<Vec<i32>>) {
        if left==0 { out.push(path.clone()); return; }
        for i in start..a.len() { if a[i]>left { break; } path.push(a[i]); visit(a,i,left-a[i],path,out); path.pop(); }
    }
    let mut a=candidates.to_vec(); assert!(a.iter().all(|&x|x>0)); a.sort_unstable(); a.dedup();
    let mut out=Vec::new(); visit(&a,0,target,&mut Vec::new(),&mut out); out
}''')
add('parentheses-generation', '''
fn parentheses(n:usize)->Vec<String> {
    fn visit(n:usize,open:usize,closed:usize,text:&mut String,out:&mut Vec<String>) {
        if closed==n { out.push(text.clone()); return; }
        if open<n { text.push('('); visit(n,open+1,closed,text,out); text.pop(); }
        if closed<open { text.push(')'); visit(n,open,closed+1,text,out); text.pop(); }
    }
    let mut out=Vec::new(); visit(n,0,0,&mut String::new(),&mut out); out
}''')
add('word-grid-search', '''
fn word_exists(grid:&[Vec<u8>],word:&[u8])->bool {
    fn search(g:&[Vec<u8>],w:&[u8],r:usize,c:usize,i:usize,seen:&mut [Vec<bool>])->bool {
        if seen[r][c] || g[r][c]!=w[i] { return false; } if i+1==w.len() { return true; }
        seen[r][c]=true; let mut found=false;
        for (dr,dc) in [(-1,0),(1,0),(0,-1),(0,1)] {
            let (a,b)=(r as isize+dr,c as isize+dc);
            if a>=0 && b>=0 && a<g.len() as isize && b<g[0].len() as isize && search(g,w,a as usize,b as usize,i+1,seen) { found=true; break; }
        }
        seen[r][c]=false; found
    }
    if word.is_empty() { return true; } if grid.is_empty() { return false; }
    let mut seen=vec![vec![false;grid[0].len()];grid.len()];
    (0..grid.len()).any(|r|(0..grid[r].len()).any(|c|search(grid,word,r,c,0,&mut seen)))
}''')
add('palindrome-partition', '''
fn palindrome_partitions(text:&str)->usize {
    assert!(text.is_ascii()); let a=text.as_bytes(); let n=a.len(); let mut palindrome=vec![vec![false;n];n];
    for i in (0..n).rev() { for j in i..n { palindrome[i][j]=a[i]==a[j] && (j-i<2 || palindrome[i+1][j-1]); } }
    fn count(i:usize,p:&[Vec<bool>])->usize {
        if i==p.len() { return 1; } (i..p.len()).filter(|&j|p[i][j]).map(|j|count(j+1,p)).sum()
    }
    count(0,&palindrome)
}''')
add('n-queens', '''
fn queens(n:usize)->usize {
    fn place(row:usize,n:usize,cols:&mut [bool],down:&mut [bool],up:&mut [bool])->usize {
        if row==n { return 1; } let mut count=0;
        for c in 0..n { let (d,u)=(row+c,row+n-1-c);
            if !cols[c] && !down[d] && !up[u] {
                cols[c]=true; down[d]=true; up[u]=true;
                count+=place(row+1,n,cols,down,up); cols[c]=false; down[d]=false; up[u]=false;
            }
        } count
    }
    if n==0 { return 1; } place(0,n,&mut vec![false;n],&mut vec![false;2*n-1],&mut vec![false;2*n-1])
}''')
add('sudoku', '''
fn solve_sudoku(grid:&mut [[u8;9];9])->bool {
    let empty=(0..9).flat_map(|r|(0..9).map(move |c|(r,c))).find(|&(r,c)|grid[r][c]==0);
    let Some((r,c))=empty else { return true; };
    for value in 1..=9 {
        let row=(0..9).all(|i|grid[r][i]!=value); let col=(0..9).all(|i|grid[i][c]!=value);
        let block=(r/3*3..r/3*3+3).all(|a|(c/3*3..c/3*3+3).all(|b|grid[a][b]!=value));
        if row && col && block { grid[r][c]=value; if solve_sudoku(grid) { return true; } grid[r][c]=0; }
    }
    false
}''')
add('meet-in-middle', '''
fn subset_exists(values:&[i32],target:i32)->bool {
    fn sums(a:&[i32])->Vec<i32> {
        let mut out=vec![0]; for &x in a { let n=out.len(); for i in 0..n { out.push(out[i]+x); } } out
    }
    let mid=values.len()/2; let left=sums(&values[..mid]); let mut right=sums(&values[mid..]); right.sort_unstable();
    left.into_iter().any(|x|right.binary_search(&(target-x)).is_ok())
}''')
add('activity-selection', '''
fn maximum_meetings(intervals:&[(i32,i32)])->usize {
    let mut sorted=intervals.to_vec(); sorted.sort_by_key(|&(s,e)|(e,s)); let mut end=i32::MIN; let mut kept=0;
    for (s,e) in sorted { if s>=end { kept+=1; end=e; } } kept
}''')
add('merge-intervals', '''
fn merged_intervals(intervals:&[(i32,i32)])->Vec<(i32,i32)> {
    let mut sorted=intervals.to_vec(); sorted.sort_unstable(); let mut out:Vec<(i32,i32)>=Vec::new();
    for (s,e) in sorted {
        if let Some(last)=out.last_mut() { if s<=last.1 { last.1=last.1.max(e); continue; } }
        out.push((s,e));
    } out
}''')
add('insert-interval', '''
fn inserted_interval(intervals:&[(i32,i32)],mut new:(i32,i32))->Vec<(i32,i32)> {
    let mut out=Vec::new(); let mut i=0;
    while i<intervals.len() && intervals[i].1<new.0 { out.push(intervals[i]); i+=1; }
    while i<intervals.len() && intervals[i].0<=new.1 { new.0=new.0.min(intervals[i].0); new.1=new.1.max(intervals[i].1); i+=1; }
    out.push(new); out.extend_from_slice(&intervals[i..]); out
}''')
add('sweep-line-events', '''
fn maximum_sessions(intervals:&[(i32,i32)])->i32 {
    let mut events=Vec::new();
    for &(start,end) in intervals { assert!(start<end); events.push((start,1)); events.push((end,-1)); }
    events.sort_unstable(); // -1 precedes +1: half-open intervals
    let (mut active,mut peak)=(0,0); for (_,delta) in events { active+=delta; peak=peak.max(active); } peak
}''')
add('jump-game', '''
fn can_reach(values:&[usize])->bool {
    if values.is_empty() { return false; } let mut farthest=0;
    for (i,&jump) in values.iter().enumerate() {
        if i>farthest { return false; } farthest=farthest.max(i+jump);
        if farthest>=values.len()-1 { return true; }
    } false
}''')
add('jump-game-two', '''
fn minimum_jumps(values:&[usize])->i32 {
    if values.is_empty() { return -1; } let (mut end,mut farthest,mut jumps)=(0,0,0);
    for i in 0..values.len()-1 {
        if i>farthest { return -1; } farthest=farthest.max(i+values[i]);
        if i==end { if farthest==end { return -1; } jumps+=1; end=farthest; if end>=values.len()-1 { break; } }
    } jumps
}''')
add('gas-station', '''
fn starting_station(gas:&[i32],cost:&[i32])->i32 {
    assert_eq!(gas.len(),cost.len()); let (mut total,mut tank,mut start)=(0,0,0);
    for i in 0..gas.len() {
        let net=gas[i]-cost[i]; total+=net; tank+=net;
        if tank<0 { tank=0; start=i+1; }
    }
    if total<0 || gas.is_empty() { -1 } else { start as i32 }
}''')
add('partition-labels', '''
fn partition_lengths(text:&str)->Vec<usize> {
    assert!(text.is_ascii()); let mut last=[0;256]; for (i,c) in text.bytes().enumerate() { last[c as usize]=i; }
    let (mut start,mut end)=(0,0); let mut out=Vec::new();
    for (i,c) in text.bytes().enumerate() { end=end.max(last[c as usize]); if i==end { out.push(i+1-start); start=i+1; } } out
}''')
add('deadline-scheduling', '''
fn maximum_profit(jobs:&[(usize,i32)])->i32 {
    fn free(parent:&mut [usize],x:usize)->usize {
        if parent[x]!=x { parent[x]=free(parent,parent[x]); } parent[x]
    }
    let mut sorted=jobs.to_vec(); sorted.sort_by_key(|&(d,p)|(std::cmp::Reverse(p),d));
    let n=jobs.len(); let mut parent:Vec<_>=(0..=n).collect(); let mut profit=0;
    for (deadline,value) in sorted {
        if value<=0 { continue; } let slot=free(&mut parent,deadline.min(n));
        if slot>0 { profit+=value; parent[slot]=free(&mut parent,slot-1); }
    } profit
}''')
add('minimum-arrows', '''
fn arrows(intervals:&[(i32,i32)])->usize {
    let mut sorted=intervals.to_vec(); sorted.sort_by_key(|&(a,b)|(b,a)); let mut last=None; let mut count=0;
    for (start,end) in sorted { if last.is_none_or(|x|start>x) { count+=1; last=Some(end); } } count
}''')
add('memoization', '''
fn fibonacci(n:usize)->u64 {
    fn compute(n:usize,memo:&mut [Option<u64>])->u64 {
        if let Some(answer)=memo[n] { return answer; }
        let answer=if n<2 { n as u64 } else { compute(n-1,memo)+compute(n-2,memo) }; memo[n]=Some(answer); answer
    }
    assert!(n<=93); compute(n,&mut vec![None;n+1])
}''')
add('tabulation', '''
fn climb_ways(n:usize)->u64 {
    let mut ways=vec![0;n+2]; ways[0]=1;
    for step in 1..=n { ways[step]=ways[step-1]+if step>=2 { ways[step-2] } else { 0 }; } ways[n]
}''')
add('rolling-dp', '''
fn stair_cost(cost:&[i32])->i32 {
    let (mut two_back,mut one_back)=(0,0);
    for &price in cost { let current=price+two_back.min(one_back); two_back=one_back; one_back=current; }
    two_back.min(one_back)
}''')
add('house-robber', '''
fn non_adjacent_sum(values:&[i32])->i32 {
    let (mut previous,mut best)=(0,0);
    for &value in values { let next=best.max(previous+value); previous=best; best=next; } best
}''')
add('kadane', '''
fn maximum_subarray(values:&[i32])->i32 {
    assert!(!values.is_empty()); let (mut ending,mut best)=(values[0],values[0]);
    for &x in &values[1..] { ending=x.max(ending+x); best=best.max(ending); } best
}''')
add('coin-change-min', '''
fn fewest_coins(coins:&[usize],amount:usize)->i32 {
    assert!(coins.iter().all(|&c|c>0)); let mut dp=vec![amount+1;amount+1]; dp[0]=0;
    for total in 1..=amount { for &coin in coins { if coin<=total { dp[total]=dp[total].min(dp[total-coin]+1); } } }
    if dp[amount]>amount { -1 } else { dp[amount] as i32 }
}''')
add('word-break-dp', '''
fn word_break(text:&str,words:&[&str])->bool {
    assert!(text.is_ascii()); let mut possible=vec![false;text.len()+1]; possible[0]=true;
    for end in 1..=text.len() {
        possible[end]=words.iter().any(|word|word.len()<=end && possible[end-word.len()] && &text[end-word.len()..end]==*word);
    } possible[text.len()]
}''')
add('decode-ways', '''
fn decodings(text:&str)->u64 {
    assert!(text.bytes().all(|c|c.is_ascii_digit())); let a=text.as_bytes(); let (mut before,mut current)=(1,1);
    for i in 0..a.len() {
        let mut next=if a[i]!=b'0' { current } else { 0 };
        if i>0 && (a[i-1]==b'1' || a[i-1]==b'2' && a[i]<=b'6') { next+=before; }
        before=current; current=next;
    } current
}''')
add('lis-patience', '''
fn lis_length(values:&[i32])->usize {
    let mut tails=Vec::new();
    for &x in values {
        let i=tails.partition_point(|&old|old<x);
        if i==tails.len() { tails.push(x); } else { tails[i]=x; }
    } tails.len()
}''')
add('zero-one-knapsack', '''
fn knapsack(weights:&[usize],values:&[i32],capacity:usize)->i32 {
    assert_eq!(weights.len(),values.len()); let mut dp=vec![0;capacity+1];
    for (&weight,&value) in weights.iter().zip(values) {
        for c in (weight..=capacity).rev() { dp[c]=dp[c].max(dp[c-weight]+value); }
    } dp[capacity]
}''')
add('grid-path-dp', '''
fn grid_paths(rows:usize,cols:usize)->u64 {
    if rows==0 || cols==0 { return 0; } let mut dp=vec![1;cols];
    for _ in 1..rows { for c in 1..cols { dp[c]+=dp[c-1]; } } dp[cols-1]
}''')
add('subset-sum', '''
fn subset_sum(values:&[usize],target:usize)->bool {
    let mut reachable=vec![false;target+1]; reachable[0]=true;
    for &x in values { for sum in (x..=target).rev() { reachable[sum]|=reachable[sum-x]; } } reachable[target]
}''')
add('longest-common-subsequence', '''
fn lcs(a:&str,b:&str)->usize {
    assert!(a.is_ascii() && b.is_ascii()); let mut dp=vec![vec![0;b.len()+1];a.len()+1];
    for (i,x) in a.bytes().enumerate() { for (j,y) in b.bytes().enumerate() {
        dp[i+1][j+1]=if x==y { dp[i][j]+1 } else { dp[i][j+1].max(dp[i+1][j]) };
    } } dp[a.len()][b.len()]
}''')
add('edit-distance', '''
fn edit_distance(a:&str,b:&str)->usize {
    assert!(a.is_ascii() && b.is_ascii()); let mut dp:Vec<_>=(0..=b.len()).collect();
    for (i,x) in a.bytes().enumerate() {
        let mut next=vec![i+1];
        for (j,y) in b.bytes().enumerate() { next.push((next[j]+1).min(dp[j+1]+1).min(dp[j]+usize::from(x!=y))); } dp=next;
    } dp[b.len()]
}''')
add('longest-pal-subsequence', '''
fn palindromic_subsequence(text:&str)->usize {
    assert!(text.is_ascii()); let a=text.as_bytes(); let n=a.len(); if n==0 { return 0; } let mut dp=vec![vec![0;n];n];
    for i in (0..n).rev() { dp[i][i]=1; for j in i+1..n {
        dp[i][j]=if a[i]==a[j] { 2+if j==i+1 { 0 } else { dp[i+1][j-1] } } else { dp[i+1][j].max(dp[i][j-1]) };
    } } dp[0][n-1]
}''')
add('matrix-chain', '''
fn matrix_chain(dimensions:&[i64])->i64 {
    assert!(dimensions.len()>=2); let n=dimensions.len()-1; let mut dp=vec![vec![0;n];n];
    for length in 2..=n { for i in 0..=n-length { let j=i+length-1; dp[i][j]=i64::MAX;
        for k in i..j { dp[i][j]=dp[i][j].min(dp[i][k]+dp[k+1][j]+dimensions[i]*dimensions[k+1]*dimensions[j+1]); }
    } } dp[0][n-1]
}''')
add('interval-dp', '''
fn balloon_coins(values:&[i32])->i32 {
    let mut a=vec![1]; a.extend_from_slice(values); a.push(1); let n=a.len(); let mut dp=vec![vec![0;n];n];
    for width in 2..n { for left in 0..n-width { let right=left+width;
        for last in left+1..right { dp[left][right]=dp[left][right].max(dp[left][last]+dp[last][right]+a[left]*a[last]*a[right]); }
    } } dp[0][n-1]
}''')
add('digit-dp', '''
fn digit_sum_count(bound:u64,target:usize)->u64 {
    fn count(pos:usize,left:usize,tight:bool,digits:&[u8],memo:&mut [Vec<Option<u64>>])->u64 {
        if pos==digits.len() { return u64::from(left==0); }
        if !tight { if let Some(answer)=memo[pos][left] { return answer; } }
        let limit=if tight { digits[pos] } else { 9 }; let mut answer=0;
        for digit in 0..=limit { if digit as usize<=left { answer+=count(pos+1,left-digit as usize,tight && digit==limit,digits,memo); } }
        if !tight { memo[pos][left]=Some(answer); } answer
    }
    let digits:Vec<_>=bound.to_string().bytes().map(|c|c-b'0').collect();
    count(0,target,true,&digits,&mut vec![vec![None;target+1];digits.len()])
}''')
add('bitmask-dp', '''
fn travelling_salesman(cost:&[Vec<i32>])->i32 {
    let n=cost.len(); assert!(n>0 && n<=16); let states=1<<n; let infinity=i32::MAX/4; let mut dp=vec![vec![infinity;n];states]; dp[1][0]=0;
    for mask in 1..states { for last in 0..n { if dp[mask][last]==infinity { continue; }
        for next in 0..n { if mask>>next&1==0 { let new=mask|1<<next; dp[new][next]=dp[new][next].min(dp[mask][last]+cost[last][next]); } }
    } }
    (0..n).map(|last|dp[states-1][last]+cost[last][0]).min().unwrap()
}''')
add('tree-dp', '''
fn tree_independent_sum(root:&Tree)->i32 {
    fn states(root:&Tree)->(i32,i32) {
        match root { None=>(0,0),Some(n)=>{
            let (li,le)=states(&n.left); let (ri,re)=states(&n.right);
            (n.value+le+re,li.max(le)+ri.max(re))
        } }
    }
    let (included,excluded)=states(root); included.max(excluded)
}''')

add('string-frequency', '''
fn first_unique_ascii(text:&str)->Option<char> {
    assert!(text.is_ascii()); let mut count=[0;256]; for c in text.bytes() { count[c as usize]+=1; }
    text.bytes().find(|&c|count[c as usize]==1).map(char::from)
}''')
add('string-two-pointers', '''
fn normalized_palindrome(text:&str)->bool {
    assert!(text.is_ascii());
    let mut symbols=text.bytes().filter(|c|c.is_ascii_alphanumeric()).map(|c|c.to_ascii_lowercase());
    while let Some(first)=symbols.next() { if let Some(last)=symbols.next_back() { if first!=last { return false; } } }
    true
}''')
add('run-length-encoding', '''
fn run_lengths(text:&str)->String {
    let mut chars=text.chars(); let Some(mut previous)=chars.next() else { return String::new(); };
    let mut length=1; let mut out=String::new();
    for current in chars {
        if current==previous { length+=1; } else { out.push(previous); out.push_str(&length.to_string()); previous=current; length=1; }
    }
    out.push(previous); out.push_str(&length.to_string()); out
}''')
add('kmp', '''
fn kmp_first(text:&str,pattern:&str)->i32 {
    let (a,p)=(text.as_bytes(),pattern.as_bytes()); if p.is_empty() { return 0; }
    let mut prefix=vec![0;p.len()];
    for i in 1..p.len() { let mut j=prefix[i-1]; while j>0 && p[i]!=p[j] { j=prefix[j-1]; } if p[i]==p[j] { j+=1; } prefix[i]=j; }
    let mut matched=0;
    for (i,&c) in a.iter().enumerate() {
        while matched>0 && c!=p[matched] { matched=prefix[matched-1]; }
        if c==p[matched] { matched+=1; } if matched==p.len() { return (i+1-p.len()) as i32; }
    }
    -1 // byte offset; exercises use ASCII
}''')
add('z-algorithm', '''
fn z_values(text:&str)->Vec<usize> {
    let a=text.as_bytes(); let n=a.len(); let mut z=vec![0;n]; let (mut left,mut right)=(0,0);
    for i in 1..n {
        if i<right { z[i]=z[i-left].min(right-i); }
        while i+z[i]<n && a[z[i]]==a[i+z[i]] { z[i]+=1; }
        if i+z[i]>right { left=i; right=i+z[i]; }
    } z // convention: z[0] is zero
}''')
add('rabin-karp', '''
fn rolling_matches(text:&str,pattern:&str)->Vec<usize> {
    let (a,p)=(text.as_bytes(),pattern.as_bytes()); let m=p.len(); if m==0 { return (0..=a.len()).collect(); } if m>a.len() { return Vec::new(); }
    let (base,modulus)=(257_u64,1_000_000_007_u64); let mut power=1;
    for _ in 1..m { power=power*base%modulus; }
    let (mut wanted,mut hash)=(0,0);
    for i in 0..m { wanted=(wanted*base+p[i] as u64)%modulus; hash=(hash*base+a[i] as u64)%modulus; }
    let mut out=Vec::new();
    for i in 0..=a.len()-m {
        if hash==wanted && &a[i..i+m]==p { out.push(i); } // verify collisions
        if i+m<a.len() { hash=((hash+modulus-a[i] as u64*power%modulus)*base+a[i+m] as u64)%modulus; }
    } out
}''')
add('trie', '''
#[derive(Default)]
struct TrieNode { children:std::collections::BTreeMap<char,usize>, pass:usize }
fn prefix_count(words:&[&str],prefix:&str)->usize {
    let mut nodes=vec![TrieNode::default()];
    for word in words {
        let mut v=0; nodes[v].pass+=1;
        for c in word.chars() {
            let u=if let Some(&u)=nodes[v].children.get(&c) { u } else { let u=nodes.len(); nodes.push(TrieNode::default()); nodes[v].children.insert(c,u); u };
            v=u; nodes[v].pass+=1;
        }
    }
    let mut v=0;
    for c in prefix.chars() { let Some(&u)=nodes[v].children.get(&c) else { return 0; }; v=u; }
    nodes[v].pass
}''')
add('aho-corasick', '''
#[derive(Clone)]
struct AutomatonNode { next:[usize;26], failure:usize, matches:usize }
fn multi_pattern_count(text:&str,patterns:&[&str])->usize {
    let empty=AutomatonNode{next:[0;26],failure:0,matches:0}; let mut nodes=vec![empty.clone()];
    for pattern in patterns {
        assert!(!pattern.is_empty()); let mut v=0;
        for c in pattern.bytes() { assert!(c.is_ascii_lowercase()); let key=(c-b'a') as usize;
            if nodes[v].next[key]==0 { nodes[v].next[key]=nodes.len(); nodes.push(empty.clone()); } v=nodes[v].next[key];
        } nodes[v].matches+=1;
    }
    let mut queue=std::collections::VecDeque::new(); for &u in &nodes[0].next { if u!=0 { queue.push_back(u); } }
    while let Some(v)=queue.pop_front() {
        let failure=nodes[v].failure; nodes[v].matches+=nodes[failure].matches;
        for c in 0..26 { let u=nodes[v].next[c];
            if u==0 { nodes[v].next[c]=nodes[failure].next[c]; }
            else { nodes[u].failure=nodes[failure].next[c]; queue.push_back(u); }
        }
    }
    let (mut state,mut count)=(0,0);
    for c in text.bytes() { assert!(c.is_ascii_lowercase()); state=nodes[state].next[(c-b'a') as usize]; count+=nodes[state].matches; } count
}''')
add('suffix-array', '''
fn suffix_array(text:&str)->Vec<usize> {
    let n=text.len(); let mut order:Vec<_>=(0..n).collect(); let mut rank:Vec<i32>=text.bytes().map(i32::from).collect(); let mut width=1;
    while width<n {
        order.sort_unstable_by_key(|&i|(rank[i],rank.get(i+width).copied().unwrap_or(-1)));
        let mut next=vec![0;n];
        for i in 1..n {
            let (a,b)=(order[i-1],order[i]); let key=|j:usize|(rank[j],rank.get(j+width).copied().unwrap_or(-1));
            next[b]=next[a]+i32::from(key(a)!=key(b));
        }
        rank=next; if n==0 || rank[order[n-1]]==n as i32-1 { break; } width*=2;
    }
    order // comparison-sort doubling: O(n log² n), byte indexes
}''')
add('manacher', '''
fn longest_palindrome(text:&str)->&str {
    assert!(text.is_ascii()); let mut symbols=vec![0_u16]; for b in text.bytes() { symbols.push(b as u16+1); symbols.push(0); }
    let n=symbols.len(); let mut radius=vec![0;n]; let (mut center,mut right)=(0,0); let (mut start,mut length)=(0,0);
    for i in 0..n {
        if i<right { radius[i]=radius[2*center-i].min(right-i); }
        while radius[i]<i && i+radius[i]+1<n && symbols[i-radius[i]-1]==symbols[i+radius[i]+1] { radius[i]+=1; }
        if i+radius[i]>right { center=i; right=i+radius[i]; }
        let candidate=(i-radius[i])/2;
        if radius[i]>length || radius[i]==length && candidate<start { start=candidate; length=radius[i]; }
    }
    &text[start..start+length]
}''')
add('euclid-gcd', '''
fn gcd(mut a:u64,mut b:u64)->u64 {
    while b!=0 { (a,b)=(b,a%b); } a
}''')
add('bitmask-enumeration', '''
fn matching_masks(values:&[i32],target:i32)->Vec<usize> {
    assert!(values.len()<usize::BITS as usize);
    (0..1_usize<<values.len()).filter(|&mask|values.iter().enumerate().filter(|(i,_)|mask>>i&1==1).map(|(_,x)|x).sum::<i32>()==target).collect()
}''')
add('xor-cancellation', '''
fn single_value(values:&[i32])->i32 {
    // Every other value occurs exactly twice.
    values.iter().fold(0,|acc,&x|acc^x)
}''')
add('sieve', '''
fn primes_to(n:usize)->Vec<usize> {
    let mut prime=vec![true;n+1]; prime[0]=false; if n>=1 { prime[1]=false; }
    let mut p=2;
    while p<=n/p { if prime[p] { for multiple in (p*p..=n).step_by(p) { prime[multiple]=false; } } p+=1; }
    (2..=n).filter(|&i|prime[i]).collect()
}''')
add('fast-power', '''
fn mod_power(mut base:u64,mut exponent:u64,modulus:u64)->u64 {
    assert!(modulus>0); let mut result=1%modulus; base%=modulus;
    while exponent>0 {
        if exponent&1==1 { result=(result as u128*base as u128%modulus as u128) as u64; }
        base=(base as u128*base as u128%modulus as u128) as u64; exponent>>=1;
    } result
}''')
add('modular-inverse', '''
fn modular_inverse(a:i64,modulus:i64)->Option<i64> {
    assert!(modulus>1); let (mut old_r,mut r)=(a.rem_euclid(modulus),modulus); let (mut old_s,mut s)=(1_i128,0_i128);
    while r!=0 {
        let q=old_r/r; (old_r,r)=(r,old_r-q*r); (old_s,s)=(s,old_s-q as i128*s);
    }
    (old_r==1).then(||old_s.rem_euclid(modulus as i128) as i64)
}''')
add('binomial-coefficients', '''
fn choose(n:u64,k:u64)->u64 {
    if k>n { return 0; } assert!(n<=60); let k=k.min(n-k); let mut answer=1_u128;
    for i in 1..=k { answer=answer*(n-k+i) as u128/i as u128; } answer as u64
}''')
add('gray-code', '''
fn gray_codes(bits:usize)->Vec<usize> {
    assert!(bits<usize::BITS as usize);
    (0..1_usize<<bits).map(|i|i^(i>>1)).collect()
}''')
add('matrix-exponentiation', '''
fn fibonacci_matrix(mut n:u64)->u64 {
    fn multiply(a:[[u64;2];2],b:[[u64;2];2])->[[u64;2];2] {
        let mut out=[[0;2];2]; for i in 0..2 { for j in 0..2 { for k in 0..2 { out[i][j]+=a[i][k]*b[k][j]; } } } out
    }
    assert!(n<=90); let mut result=[[1,0],[0,1]]; let mut power=[[1,1],[1,0]];
    while n>0 { if n&1==1 { result=multiply(result,power); } n>>=1; if n>0 { power=multiply(power,power); } }
    result[0][1]
}''')
add('miller-rabin', '''
fn is_prime(n:u64)->bool {
    fn power(mut a:u64,mut d:u64,n:u64)->u64 {
        let mut result=1; while d>0 { if d&1==1 { result=(result as u128*a as u128%n as u128) as u64; } a=(a as u128*a as u128%n as u128) as u64; d>>=1; } result
    }
    if n<2 { return false; } for p in [2,3,5,7,11,13,17,19,23,29,31,37] { if n%p==0 { return n==p; } }
    let shifts=(n-1).trailing_zeros(); let d=(n-1)>>shifts;
    // These seven bases cover unsigned 64-bit integers; u128 avoids overflow.
    for a in [2,325,9375,28178,450775,9780504,1795265022] {
        if a%n==0 { continue; } let mut x=power(a%n,d,n); if x==1 || x==n-1 { continue; }
        let mut witness=true; for _ in 1..shifts { x=(x as u128*x as u128%n as u128) as u64; if x==n-1 { witness=false; break; } }
        if witness { return false; }
    } true
}''')

add('sparse-table', '''
fn sparse_minima(values:&[i32],queries:&[(usize,usize)])->Vec<i32> {
    assert!(!values.is_empty()); let n=values.len(); let mut levels=vec![values.to_vec()]; let mut width=2;
    while width<=n {
        let previous=levels.last().unwrap(); let half=width/2;
        levels.push((0..=n-width).map(|i|previous[i].min(previous[i+half])).collect()); width*=2;
    }
    queries.iter().map(|&(left,right)| {
        let length=right-left+1; let level=length.ilog2() as usize; let width=1<<level;
        levels[level][left].min(levels[level][right+1-width])
    }).collect()
}''')
add('disjoint-set-union', '''
fn components_after_unions(n:usize,unions:&[(usize,usize)])->usize {
    let mut sets=Dsu::new(n); for &(a,b) in unions { sets.join(a,b); } sets.count
}''')
add('lazy-segment-tree', '''
struct LazySum { sum:Vec<i64>, lazy:Vec<i64>, n:usize }
impl LazySum {
    fn new(values:&[i64])->Self {
        let n=values.len(); assert!(n>0); let mut tree=Self{sum:vec![0;4*n],lazy:vec![0;4*n],n};
        fn build(t:&mut LazySum,v:usize,left:usize,right:usize,a:&[i64]) {
            if right-left==1 { t.sum[v]=a[left]; } else { let mid=(left+right)/2; build(t,v*2,left,mid,a); build(t,v*2+1,mid,right,a); t.sum[v]=t.sum[v*2]+t.sum[v*2+1]; }
        }
        build(&mut tree,1,0,n,values); tree
    }
    fn apply(&mut self,v:usize,length:usize,delta:i64) { self.sum[v]+=delta*length as i64; self.lazy[v]+=delta; }
    fn push(&mut self,v:usize,left:usize,right:usize) {
        if right-left>1 { let mid=(left+right)/2; let d=self.lazy[v]; self.apply(v*2,mid-left,d); self.apply(v*2+1,right-mid,d); } self.lazy[v]=0;
    }
    fn update(&mut self,v:usize,left:usize,right:usize,from:usize,to:usize,delta:i64) {
        if to<=left || right<=from { return; } if from<=left && right<=to { self.apply(v,right-left,delta); return; }
        self.push(v,left,right); let mid=(left+right)/2;
        self.update(v*2,left,mid,from,to,delta); self.update(v*2+1,mid,right,from,to,delta); self.sum[v]=self.sum[v*2]+self.sum[v*2+1];
    }
    fn query(&mut self,v:usize,left:usize,right:usize,from:usize,to:usize)->i64 {
        if to<=left || right<=from { return 0; } if from<=left && right<=to { return self.sum[v]; }
        self.push(v,left,right); let mid=(left+right)/2;
        self.query(v*2,left,mid,from,to)+self.query(v*2+1,mid,right,from,to)
    }
    fn add(&mut self,left:usize,right:usize,delta:i64) { self.update(1,0,self.n,left,right+1,delta); }
    fn range_sum(&mut self,left:usize,right:usize)->i64 { self.query(1,0,self.n,left,right+1) }
}
fn lazy_example(values:&[i64])->i64 { let mut tree=LazySum::new(values); tree.add(1,4,3); tree.range_sum(2,5) }
''')
add('treap', '''
type TreapLink=Option<Box<TreapNode>>;
struct TreapNode { key:i32, priority:u64, left:TreapLink, right:TreapLink }
fn merge_treaps(a:TreapLink,b:TreapLink)->TreapLink {
    match (a,b) {
        (None,b)=>b,(a,None)=>a,
        (Some(mut a),Some(mut b))=>if a.priority>b.priority {
            a.right=merge_treaps(a.right.take(),Some(b)); Some(a)
        } else { b.left=merge_treaps(Some(a),b.left.take()); Some(b) }
    }
}
fn treap_insert(root:TreapLink,key:i32,priority:u64)->TreapLink {
    let Some(mut n)=root else { return Some(Box::new(TreapNode{key,priority,left:None,right:None})); };
    if key==n.key { return Some(n); }
    if key<n.key {
        n.left=treap_insert(n.left.take(),key,priority);
        if n.left.as_ref().unwrap().priority>n.priority { let mut top=n.left.take().unwrap(); n.left=top.right.take(); top.right=Some(n); return Some(top); }
    } else {
        n.right=treap_insert(n.right.take(),key,priority);
        if n.right.as_ref().unwrap().priority>n.priority { let mut top=n.right.take().unwrap(); n.right=top.left.take(); top.left=Some(n); return Some(top); }
    } Some(n)
}
fn treap_delete(root:TreapLink,key:i32)->TreapLink {
    let Some(mut n)=root else { return None; };
    if key==n.key { return merge_treaps(n.left.take(),n.right.take()); }
    if key<n.key { n.left=treap_delete(n.left.take(),key); } else { n.right=treap_delete(n.right.take(),key); } Some(n)
}
fn treap_operations(ops:&[(bool,i32)])->Vec<i32> {
    let mut root=None; let mut random=0xC0FFEE_u64;
    for &(insert,key) in ops {
        random^=random<<13; random^=random>>7; random^=random<<17;
        root=if insert { treap_insert(root,key,random) } else { treap_delete(root,key) };
    }
    fn walk(root:&TreapLink,out:&mut Vec<i32>) { if let Some(n)=root { walk(&n.left,out); out.push(n.key); walk(&n.right,out); } }
    let mut out=Vec::new(); walk(&root,&mut out); out
}''')
add('skip-list', '''
struct SkipNode { key:i32, next:Vec<Option<usize>> }
fn skip_contains(values:&[i32],target:i32)->bool {
    const LEVELS:usize=32;
    let mut nodes=vec![SkipNode{key:i32::MIN,next:vec![None;LEVELS]}]; let mut random=0xC0FFEE_u64;
    for &key in values {
        let mut update=[0;LEVELS]; let mut v=0;
        for level in (0..LEVELS).rev() {
            while let Some(u)=nodes[v].next[level] { if nodes[u].key>=key { break; } v=u; } update[level]=v;
        }
        if nodes[v].next[0].is_some_and(|u|nodes[u].key==key) { continue; }
        let mut height=1;
        while height<LEVELS {
            random^=random<<13; random^=random>>7; random^=random<<17;
            if random&1==0 { break; } height+=1;
        }
        let index=nodes.len(); let next=(0..height).map(|level|nodes[update[level]].next[level]).collect();
        nodes.push(SkipNode{key,next}); for level in 0..height { nodes[update[level]].next[level]=Some(index); }
    }
    let mut v=0;
    for level in (0..LEVELS).rev() { while let Some(u)=nodes[v].next[level] { if nodes[u].key>=target { break; } v=u; } }
    nodes[v].next[0].is_some_and(|u|nodes[u].key==target)
}''')
add('dsu-rollback', '''
struct RollbackDsu { parent:Vec<usize>, size:Vec<usize>, history:Vec<(usize,usize,usize)> }
impl RollbackDsu {
    fn new(n:usize)->Self { Self{parent:(0..n).collect(),size:vec![1;n],history:Vec::new()} }
    fn root(&self,mut v:usize)->usize { while v!=self.parent[v] { v=self.parent[v]; } v }
    fn join(&mut self,a:usize,b:usize) {
        let (mut a,mut b)=(self.root(a),self.root(b)); if a==b { return; }
        if self.size[a]<self.size[b] { std::mem::swap(&mut a,&mut b); }
        self.history.push((b,a,self.size[a])); self.parent[b]=a; self.size[a]+=self.size[b];
    }
    fn checkpoint(&self)->usize { self.history.len() }
    fn rollback(&mut self,mark:usize) {
        while self.history.len()>mark { let (b,a,size)=self.history.pop().unwrap(); self.parent[b]=b; self.size[a]=size; }
    }
}
fn rollback_query(n:usize,before:&[(usize,usize)],after:&[(usize,usize)],query:(usize,usize))->bool {
    let mut dsu=RollbackDsu::new(n); for &(a,b) in before { dsu.join(a,b); } let mark=dsu.checkpoint();
    for &(a,b) in after { dsu.join(a,b); } dsu.rollback(mark); dsu.root(query.0)==dsu.root(query.1)
}''')
add('mo-algorithm', '''
fn distinct_queries(values:&[i32],queries:&[(usize,usize)])->Vec<usize> {
    let block=(values.len() as f64).sqrt().max(1.0) as usize;
    let mut order:Vec<_>=(0..queries.len()).collect(); order.sort_by_key(|&i|{let (l,r)=queries[i]; (l/block,if l/block%2==0 {r as isize} else {-(r as isize)})});
    let mut counts=std::collections::HashMap::<i32,usize>::new(); let (mut left,mut right,mut distinct)=(0,0,0); let mut out=vec![0;queries.len()];
    fn change(counts:&mut std::collections::HashMap<i32,usize>,distinct:&mut usize,x:i32,add:bool) {
        let count=counts.entry(x).or_default();
        if add { if *count==0 {*distinct+=1;} *count+=1; } else { *count-=1; if *count==0 {*distinct-=1;} }
    }
    for i in order { let (l,r)=queries[i]; let end=r+1;
        while left>l { left-=1; change(&mut counts,&mut distinct,values[left],true); }
        while right<end { change(&mut counts,&mut distinct,values[right],true); right+=1; }
        while left<l { change(&mut counts,&mut distinct,values[left],false); left+=1; }
        while right>end { right-=1; change(&mut counts,&mut distinct,values[right],false); }
        out[i]=distinct;
    } out
}''')
add('heavy-light', '''
fn heavy_light_sum(graph:&[Vec<usize>],values:&[i64],mut a:usize,mut b:usize)->i64 {
    fn sizes(v:usize,p:usize,g:&[Vec<usize>],parent:&mut [usize],depth:&mut [usize],size:&mut [usize],heavy:&mut [usize]) {
        parent[v]=p; size[v]=1;
        for &u in &g[v] { if u!=p {
            depth[u]=depth[v]+1; sizes(u,v,g,parent,depth,size,heavy); size[v]+=size[u];
            if heavy[v]==g.len() || size[u]>size[heavy[v]] { heavy[v]=u; }
        } }
    }
    fn split(v:usize,h:usize,g:&[Vec<usize>],parent:&[usize],heavy:&[usize],head:&mut [usize],position:&mut [usize],timer:&mut usize) {
        head[v]=h; position[v]=*timer; *timer+=1;
        if heavy[v]!=g.len() { split(heavy[v],h,g,parent,heavy,head,position,timer); }
        for &u in &g[v] { if u!=parent[v] && u!=heavy[v] { split(u,u,g,parent,heavy,head,position,timer); } }
    }
    let n=graph.len(); let (mut parent,mut depth,mut size,mut heavy)=(vec![n;n],vec![0;n],vec![0;n],vec![n;n]);
    sizes(0,n,graph,&mut parent,&mut depth,&mut size,&mut heavy);
    let (mut head,mut position)=(vec![0;n],vec![0;n]); split(0,0,graph,&parent,&heavy,&mut head,&mut position,&mut 0);
    let mut bit=vec![0;n+1];
    for v in 0..n { let mut i=position[v]+1; while i<=n { bit[i]+=values[v]; i+=i&i.wrapping_neg(); } }
    let prefix=|mut i:usize| { let mut sum=0; while i>0 { sum+=bit[i]; i&=i-1; } sum };
    let mut sum=0;
    while head[a]!=head[b] {
        if depth[head[a]]<depth[head[b]] { std::mem::swap(&mut a,&mut b); }
        sum+=prefix(position[a]+1)-prefix(position[head[a]]); a=parent[head[a]];
    }
    let (left,right)=(position[a].min(position[b]),position[a].max(position[b])); sum+prefix(right+1)-prefix(left)
}''')
add('centroid-decomposition', '''
fn centroid_root(graph:&[Vec<usize>])->usize {
    fn collect(v:usize,p:usize,g:&[Vec<usize>],blocked:&[bool],sizes:&mut [usize],members:&mut Vec<usize>) {
        sizes[v]=1; members.push(v);
        for &u in &g[v] { if u!=p && !blocked[u] { collect(u,v,g,blocked,sizes,members); sizes[v]+=sizes[u]; } }
    }
    fn decompose(start:usize,parent:Option<usize>,g:&[Vec<usize>],blocked:&mut [bool],answer:&mut [Option<usize>],sizes:&mut [usize]) {
        let mut members=Vec::new(); collect(start,g.len(),g,blocked,sizes,&mut members); let total=members.len();
        let centroid=*members.iter().filter(|&&v| {
            let mut largest=total-sizes[v];
            for &u in &g[v] { if !blocked[u] && sizes[u]<sizes[v] { largest=largest.max(sizes[u]); } }
            largest<=total/2
        }).min().unwrap();
        answer[centroid]=parent; blocked[centroid]=true;
        for &u in &g[centroid] { if !blocked[u] { decompose(u,Some(centroid),g,blocked,answer,sizes); } }
    }
    assert!(!graph.is_empty()); let mut parents=vec![None;graph.len()];
    decompose(0,None,graph,&mut vec![false;graph.len()],&mut parents,&mut vec![0;graph.len()]); parents.iter().position(Option::is_none).unwrap()
}''')
add('suffix-automaton', '''
#[derive(Clone)]
struct SuffixState { length:usize, link:Option<usize>, next:std::collections::BTreeMap<u8,usize> }
fn distinct_substrings(text:&str)->usize {
    let empty=SuffixState{length:0,link:None,next:std::collections::BTreeMap::new()}; let mut states=vec![empty.clone()]; let mut last=0;
    for c in text.bytes() {
        let current=states.len(); states.push(SuffixState{length:states[last].length+1,..empty.clone()}); let mut p=Some(last);
        while let Some(v)=p { if states[v].next.contains_key(&c) { break; } states[v].next.insert(c,current); p=states[v].link; }
        if let Some(v)=p {
            let q=states[v].next[&c];
            if states[v].length+1==states[q].length { states[current].link=Some(q); }
            else {
                let clone=states.len(); let mut copied=states[q].clone(); copied.length=states[v].length+1; states.push(copied);
                while let Some(v)=p { if states[v].next.get(&c)!=Some(&q) { break; } states[v].next.insert(c,clone); p=states[v].link; }
                states[q].link=Some(clone); states[current].link=Some(clone);
            }
        } else { states[current].link=Some(0); }
        last=current;
    }
    states.iter().skip(1).map(|s|s.length-states[s.link.unwrap()].length).sum()
}''')
