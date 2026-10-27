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
}

fn main() {
    let result = prefix_count(&["crab","crate","rust"],"cr").to_string();
    println!("{result}");
}
