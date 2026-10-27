
type Tree=Option<Box<Node>>;
struct Node { value:i32, left:Tree, right:Tree }
fn node(value:i32,left:Tree,right:Tree)->Tree { Some(Box::new(Node{value,left,right})) }
fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn inorder(root:&Tree)->Vec<i32> {
    fn visit(root:&Tree,out:&mut Vec<i32>) {
        if let Some(n)=root { visit(&n.left,out); out.push(n.value); visit(&n.right,out); }
    }
    let mut out=Vec::new(); visit(root,&mut out); out
}

fn main() {
    let result = csv(inorder(&node(4,node(2,node(1,None,None),node(3,None,None)),node(6,node(5,None,None),node(7,None,None)))));
    println!("{result}");
}
