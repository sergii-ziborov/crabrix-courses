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
}

fn main() {
    let result = copied_pairs(&[7,13,11],&[None,Some(0),Some(1)]);
    println!("{result}");
}
