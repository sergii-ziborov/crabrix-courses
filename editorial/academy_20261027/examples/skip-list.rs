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
}

fn main() {
    let result = skip_contains(&[3,6,7,9,12,19,17,26,21,25],19).to_string();
    println!("{result}");
}
