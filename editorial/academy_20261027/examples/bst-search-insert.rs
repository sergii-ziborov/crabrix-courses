
type Tree=Option<Box<Node>>;
struct Node { value:i32, left:Tree, right:Tree }
fn node(value:i32,left:Tree,right:Tree)->Tree { Some(Box::new(Node{value,left,right})) }
fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
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

fn main() {
    let result = { let mut root=node(4,node(2,node(1,None,None),node(3,None,None)),node(7,None,None)); insert_bst(&mut root,5); csv(bst_values(&root)) };
    println!("{result}");
}
