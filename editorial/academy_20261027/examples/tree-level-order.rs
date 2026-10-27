type Tree = Option<Box<Node>>;
struct Node {
    value: i32,
    left: Tree,
    right: Tree,
}
fn node(value: i32, left: Tree, right: Tree) -> Tree {
    Some(Box::new(Node { value, left, right }))
}
fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn level_sums(root: &Tree) -> Vec<i32> {
    let mut queue = std::collections::VecDeque::new();
    let mut out = Vec::new();
    if let Some(n) = root {
        queue.push_back(n.as_ref());
    }
    while !queue.is_empty() {
        let mut sum = 0;
        for _ in 0..queue.len() {
            let n = queue.pop_front().unwrap();
            sum += n.value;
            if let Some(left) = &n.left {
                queue.push_back(left);
            }
            if let Some(right) = &n.right {
                queue.push_back(right);
            }
        }
        out.push(sum);
    }
    out
}

fn main() {
    let result = csv(level_sums(&node(
        1,
        node(2, node(4, None, None), node(5, None, None)),
        node(3, None, node(6, None, None)),
    )));
    println!("{result}");
}
