type Tree = Option<Box<Node>>;
struct Node {
    value: i32,
    left: Tree,
    right: Tree,
}
fn node(value: i32, left: Tree, right: Tree) -> Tree {
    Some(Box::new(Node { value, left, right }))
}
fn tree_independent_sum(root: &Tree) -> i32 {
    fn states(root: &Tree) -> (i32, i32) {
        match root {
            None => (0, 0),
            Some(n) => {
                let (li, le) = states(&n.left);
                let (ri, re) = states(&n.right);
                (n.value + le + re, li.max(le) + ri.max(re))
            }
        }
    }
    let (included, excluded) = states(root);
    included.max(excluded)
}

fn main() {
    let result = tree_independent_sum(&node(
        3,
        node(2, None, node(3, None, None)),
        node(3, None, node(1, None, None)),
    ))
    .to_string();
    println!("{result}");
}
