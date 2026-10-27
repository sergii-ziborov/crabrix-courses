
type Tree=Option<Box<Node>>;
struct Node { value:i32, left:Tree, right:Tree }
fn node(value:i32,left:Tree,right:Tree)->Tree { Some(Box::new(Node{value,left,right})) }
fn ancestor(root:&Tree,a:i32,b:i32)->Option<i32> {
    // Contract: both distinct target values exist in the tree and are unique.
    match root {
        None=>None,
        Some(n) if n.value==a || n.value==b=>Some(n.value),
        Some(n)=>match (ancestor(&n.left,a,b),ancestor(&n.right,a,b)) {
            (Some(_),Some(_))=>Some(n.value),(left,right)=>left.or(right)
        }
    }
}

fn main() {
    let result = ancestor(&node(3,node(5,node(6,None,None),node(2,node(7,None,None),node(4,None,None))),node(1,node(0,None,None),node(8,None,None))),5,1).unwrap().to_string();
    println!("{result}");
}
