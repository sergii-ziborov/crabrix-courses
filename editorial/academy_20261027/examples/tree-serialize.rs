
type Tree=Option<Box<Node>>;
struct Node { value:i32, left:Tree, right:Tree }
fn node(value:i32,left:Tree,right:Tree)->Tree { Some(Box::new(Node{value,left,right})) }
fn serialize(root:&Tree)->String {
    fn visit(root:&Tree,out:&mut Vec<String>) {
        match root { None=>out.push("#".into()),Some(n)=>{
            out.push(n.value.to_string()); visit(&n.left,out); visit(&n.right,out);
        } }
    }
    let mut out=Vec::new(); visit(root,&mut out); out.join(",")
}

fn main() {
    let result = serialize(&node(1,node(2,None,None),node(3,node(4,None,None),node(5,None,None))));
    println!("{result}");
}
