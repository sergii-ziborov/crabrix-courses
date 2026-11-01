"""Rust cores that replace or extend the 27 October Atlas programs.

Each entry supersedes the same key in academy_20261027/rust_sources.py. The old
module stays untouched as the record of that pass.
"""

PROGRAMS = {}

PROGRAMS['remove-nth-from-end'] = '''
struct ListNode { value:i32, next:Option<usize> }
fn arena(values:&[i32])->Vec<ListNode> {
    values.iter().enumerate().map(|(i,&value)|ListNode{value,next:(i+1<values.len()).then_some(i+1)}).collect()
}
// Rust rejects a shared lead reference and a mutable trail reference into one
// Box chain. Two indexes into an arena can move together without that conflict.
fn remove_from_end(nodes:&mut [ListNode],head:usize,n:usize)->Option<usize> {
    // Open a gap of n links between the two cursors, without measuring the list.
    let mut lead=Some(head);
    for _ in 0..n { lead=nodes[lead.expect("n is at most the list length")].next; }
    // Lead fell off the end during the gap, so the target is the head itself.
    let Some(mut lead)=lead else { return nodes[head].next; };
    // Move both until lead is on the last node; trail then sits before the target.
    let mut trail=head;
    while let Some(next)=nodes[lead].next { lead=next; trail=nodes[trail].next.unwrap(); }
    let target=nodes[trail].next.unwrap();
    nodes[trail].next=nodes[target].next;
    Some(head)
}
fn remaining_values(values:&[i32],n:usize)->Vec<i32> {
    let mut nodes=arena(values); let mut cursor=remove_from_end(&mut nodes,0,n);
    let mut out=Vec::new();
    while let Some(i)=cursor { out.push(nodes[i].value); cursor=nodes[i].next; }
    out
}
'''

PROGRAMS['copy-random-list'] = '''
struct RandomNode { value:i32, next:Option<usize>, random:Option<usize> }
fn deep_copy(arena:&[RandomNode],head:Option<usize>)->Vec<RandomNode> {
    // First pass: give every source node a slot in the new arena, in list order.
    let mut slot=std::collections::HashMap::new(); let mut copy=Vec::new();
    let mut cursor=head;
    while let Some(old)=cursor {
        slot.insert(old,copy.len());
        copy.push(RandomNode{value:arena[old].value,next:None,random:None});
        cursor=arena[old].next;
    }
    // Second pass: an old index names a source node, so translate every link.
    let mut cursor=head;
    while let Some(old)=cursor {
        let new=slot[&old];
        copy[new].next=arena[old].next.map(|n|slot[&n]);
        copy[new].random=arena[old].random.map(|r|slot[&r]);
        cursor=arena[old].next;
    }
    copy
}
fn copied_pairs(values:&[i32],next:&[Option<usize>],random:&[Option<usize>])->String {
    let original:Vec<_>=values.iter().enumerate().map(|(i,&value)|RandomNode{value,next:next[i],random:random[i]}).collect();
    let mut copy=deep_copy(&original,(!original.is_empty()).then_some(0));
    let out=copy.iter().map(|n|format!("{}:{}",n.value,n.random.map_or("null".into(),|i|i.to_string()))).collect::<Vec<_>>().join(",");
    // The copy owns separate nodes, so changing it leaves the source untouched.
    if !copy.is_empty() { copy[0].value+=1; assert_ne!(original[0].value,copy[0].value); }
    out
}
'''

PROGRAMS['rolling-fingerprint'] = '''
const BASE:u64=10;
const MODULUS:u64=101;
fn window_hash(digits:&[u64],k:usize)->u64 {
    assert!(k>0);
    // Weight of the oldest digit once the window holds k digits.
    let oldest_weight=(1..k).fold(1,|weight,_|weight*BASE%MODULUS);
    let mut hash=0;
    for (i,&digit) in digits.iter().enumerate() {
        assert!(digit<10);
        if i>=k {
            // Remove the outgoing digit's contribution, then shift in the new one.
            let outgoing=digits[i-k]*oldest_weight%MODULUS;
            hash=(hash+MODULUS-outgoing)%MODULUS;
        }
        hash=(hash*BASE+digit)%MODULUS;
    }
    hash // A fingerprint is not a collision-free identity.
}
'''

PROGRAMS['rolling-window-statistic'] = '''
fn window_stats(values:&[i64],k:usize)->Vec<(i64,i64)> {
    assert!(k>0 && k<=values.len());
    let width=k as i64;
    // Sum and sum of squares stay exact; only the reported values are rounded down.
    let mut sum:i64=values[..k].iter().sum();
    let mut squares:i64=values[..k].iter().map(|x|x*x).sum();
    let report=|sum:i64,squares:i64|(sum.div_euclid(width),(width*squares-sum*sum).div_euclid(width*width));
    let mut result=vec![report(sum,squares)];
    for i in k..values.len() {
        sum+=values[i]-values[i-k];
        squares+=values[i]*values[i]-values[i-k]*values[i-k];
        result.push(report(sum,squares));
    }
    result
}
fn window_means(values:&[i64],k:usize)->Vec<i64> { window_stats(values,k).into_iter().map(|s|s.0).collect() }
fn window_variances(values:&[i64],k:usize)->Vec<i64> { window_stats(values,k).into_iter().map(|s|s.1).collect() }
'''

PROGRAMS['tree-serialize'] = '''
fn serialize(root:&Tree)->String {
    fn visit(root:&Tree,out:&mut Vec<String>) {
        match root { None=>out.push("#".into()),Some(n)=>{
            out.push(n.value.to_string()); visit(&n.left,out); visit(&n.right,out);
        } }
    }
    let mut out=Vec::new(); visit(root,&mut out); out.join(",")
}
fn deserialize(text:&str)->Tree {
    // Tokens arrive in the same preorder, so each # closes exactly one child.
    fn build<'a>(tokens:&mut impl Iterator<Item=&'a str>)->Tree {
        match tokens.next() {
            None|Some("#")=>None,
            Some(token)=>{
                let value=token.parse().unwrap();
                let left=build(tokens); let right=build(tokens);
                node(value,left,right)
            }
        }
    }
    build(&mut text.split(','))
}
fn round_trip(root:&Tree)->String {
    let text=serialize(root);
    assert_eq!(serialize(&deserialize(&text)),text);
    text
}
fn inorder_values(root:&Tree)->Vec<i32> {
    match root { None=>Vec::new(),Some(n)=>{
        let mut out=inorder_values(&n.left); out.push(n.value); out.extend(inorder_values(&n.right)); out
    } }
}
'''

PROGRAMS['hash-frequency'] = '''
fn anagrams(a: &str, b: &str) -> bool {
    assert!(a.bytes().chain(b.bytes()).all(|c| c.is_ascii_lowercase()));
    let mut counts = std::collections::HashMap::<char, i32>::new();
    for c in a.chars() { *counts.entry(c).or_default() += 1; }
    for c in b.chars() { *counts.entry(c).or_default() -= 1; }
    counts.values().all(|&n| n == 0)
}
'''

PROGRAMS['a-star'] = '''
fn grid_a_star(rows:usize,cols:usize,start:(usize,usize),goal:(usize,usize),walls:&[(usize,usize)])->Option<usize> {
    let heuristic=|(r,c):(usize,usize)|r.abs_diff(goal.0)+c.abs_diff(goal.1);
    let mut distance=vec![vec![usize::MAX;cols];rows]; distance[start.0][start.1]=0;
    let mut heap=std::collections::BinaryHeap::from([std::cmp::Reverse((heuristic(start),0,start))]);
    while let Some(std::cmp::Reverse((_,cost,(r,c))))=heap.pop() {
        if cost!=distance[r][c] { continue; } if (r,c)==goal { return Some(cost); }
        for (dr,dc) in [(-1,0),(1,0),(0,-1),(0,1)] {
            let (nr,nc)=(r as isize+dr,c as isize+dc);
            if nr<0 || nc<0 || nr>=rows as isize || nc>=cols as isize { continue; }
            let next=(nr as usize,nc as usize);
            if walls.contains(&next) { continue; }
            if cost+1<distance[next.0][next.1] { distance[next.0][next.1]=cost+1; heap.push(std::cmp::Reverse((cost+1+heuristic(next),cost+1,next))); }
        }
    }
    None
}
'''

PROGRAMS['bidirectional-bfs'] = '''
fn ladder_length(start:&str,goal:&str,words:&[&str])->usize {
    use std::collections::{HashMap,HashSet};
    // Every word after the start must come from the list, including the goal.
    if !words.contains(&goal) { return 0; }
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
}
'''

PROGRAMS['lazy-heap-deletion'] = '''
fn valid_min(ops:&[&str])->Option<i32> {
    let mut heap=std::collections::BinaryHeap::new(); let mut deleted=std::collections::HashMap::<i32,usize>::new();
    for op in ops {
        if let Some(raw)=op.strip_prefix("push") { heap.push(std::cmp::Reverse(raw.parse::<i32>().unwrap())); }
        if let Some(raw)=op.strip_prefix("delete") { *deleted.entry(raw.parse().unwrap()).or_default()+=1; }
        while let Some(&std::cmp::Reverse(x))=heap.peek() {
            let count=deleted.entry(x).or_default(); if *count==0 { break; } *count-=1; heap.pop();
        }
    }
    heap.peek().map(|top|top.0)
}
'''

PROGRAMS['min-max-tracking'] = '''
fn spread(values: &[i32]) -> i64 {
    assert!(!values.is_empty());
    let (mut low, mut high) = (values[0], values[0]);
    for &x in &values[1..] { low = low.min(x); high = high.max(x); }
    // Two i32 readings can differ by more than i32 can hold.
    i64::from(high) - i64::from(low)
}
'''

PROGRAMS['list-cycle'] = '''
fn contains_cycle(next:&[Option<usize>])->bool {
    // Arena indexes preserve node identity; None terminates a list.
    let head=(!next.is_empty()).then_some(0);
    let (mut slow,mut fast)=(head,head);
    loop {
        slow=slow.and_then(|i|next[i]); fast=fast.and_then(|i|next[i]).and_then(|i|next[i]);
        if fast.is_none() { return false; } if slow==fast { return true; }
    }
}
'''

PROGRAMS['insertion-sort'] = '''
fn insertion_sort_by_key<T:Clone,K:Ord>(values:&mut [T],key:impl Fn(&T)->K) {
    for i in 1..values.len() {
        let value=values[i].clone(); let mut j=i;
        // A strict comparison leaves an equal earlier key in front.
        while j>0 && key(&values[j-1])>key(&value) { values[j]=values[j-1].clone(); j-=1; }
        values[j]=value;
    }
}
fn insertion_sort(values:&mut [i32]) { insertion_sort_by_key(values,|x|*x); }
'''

PROGRAMS['bst-search-insert'] = '''
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
}
fn bst_preorder(root:&Tree)->Vec<i32> {
    match root { None=>Vec::new(),Some(n)=>{
        let mut out=vec![n.value]; out.extend(bst_preorder(&n.left)); out.extend(bst_preorder(&n.right)); out
    } }
}
'''

PROGRAMS['permutations'] = '''
fn permutations(values:&[i32])->Vec<Vec<i32>> {
    fn choose(values:&[i32],used:&mut [bool],path:&mut Vec<i32>,out:&mut Vec<Vec<i32>>) {
        if path.len()==values.len() { out.push(path.clone()); return; }
        for i in 0..values.len() {
            if !used[i] {
                used[i]=true; path.push(values[i]);
                choose(values,used,path,out);
                path.pop(); used[i]=false;
            }
        }
    }
    let mut out=Vec::new();
    choose(values,&mut vec![false;values.len()],&mut Vec::new(),&mut out);
    out
}
fn permutation_count(values:&[i32])->usize { permutations(values).len() }
'''
