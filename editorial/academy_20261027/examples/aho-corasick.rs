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
}

fn main() {
    let result = multi_pattern_count("ahishers",&["he","she","his","hers"]).to_string();
    println!("{result}");
}
