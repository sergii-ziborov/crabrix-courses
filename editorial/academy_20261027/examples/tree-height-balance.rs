type Tree = Option<Box<Node>>;
struct Node {
    value: i32,
    left: Tree,
    right: Tree,
}
fn node(value: i32, left: Tree, right: Tree) -> Tree {
    Some(Box::new(Node { value, left, right }))
}
fn is_balanced(root: &Tree) -> bool {
    fn height(root: &Tree) -> Option<usize> {
        match root {
            None => Some(0),
            Some(n) => {
                let (left, right) = (height(&n.left)?, height(&n.right)?);
                (left.abs_diff(right) <= 1).then_some(1 + left.max(right))
            }
        }
    }
    height(root).is_some()
}

fn main() {
    let result = is_balanced(&node(
        3,
        node(9, None, None),
        node(20, node(15, None, None), node(7, None, None)),
    ))
    .to_string();
    println!("{result}");
}
