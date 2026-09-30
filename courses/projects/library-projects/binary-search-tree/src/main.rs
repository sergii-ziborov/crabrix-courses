#[derive(Default)]
struct Node {
    value: i32,
    left: Option<Box<Node>>,
    right: Option<Box<Node>>,
}

impl Node {
    fn new(value: i32) -> Self {
        Node { value, left: None, right: None }
    }

    fn insert(&mut self, value: i32) {
        let branch = if value < self.value {
            &mut self.left
        } else {
            &mut self.right
        };
        match branch {
            Some(node) => node.insert(value),
            None => *branch = Some(Box::new(Node::new(value))),
        }
    }

    fn in_order(&self, out: &mut Vec<i32>) {
        if let Some(left) = &self.left {
            left.in_order(out);
        }
        out.push(self.value);
        if let Some(right) = &self.right {
            right.in_order(out);
        }
    }

    fn depth(&self) -> usize {
        let left = self.left.as_ref().map_or(0, |n| n.depth());
        let right = self.right.as_ref().map_or(0, |n| n.depth());
        1 + left.max(right)
    }
}

fn main() {
    let mut root = Node::new(50);
    for value in [30, 70, 20, 40, 60, 80, 35, 45] {
        root.insert(value);
    }

    let mut sorted = Vec::new();
    root.in_order(&mut sorted);
    println!("in order  {sorted:?}");
    println!("depth     {}", root.depth());
}