type Tree = Option<Box<Node>>;
struct Node {
    value: i32,
    left: Tree,
    right: Tree,
}
fn node(value: i32, left: Tree, right: Tree) -> Tree {
    Some(Box::new(Node { value, left, right }))
}
fn diameter(root: &Tree) -> usize {
    fn height(root: &Tree, best: &mut usize) -> usize {
        match root {
            None => 0,
            Some(n) => {
                let left = height(&n.left, best);
                let right = height(&n.right, best);
                *best = (*best).max(left + right);
                1 + left.max(right)
            }
        }
    }
    let mut best = 0;
    height(root, &mut best);
    best
}

fn main() {
    let result = diameter(&node(
        1,
        node(2, node(4, None, None), node(5, None, None)),
        node(3, None, None),
    ))
    .to_string();
    println!("{result}");
}
