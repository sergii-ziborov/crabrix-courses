fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
type TreapLink = Option<Box<TreapNode>>;
struct TreapNode {
    key: i32,
    priority: u64,
    left: TreapLink,
    right: TreapLink,
}
fn merge_treaps(a: TreapLink, b: TreapLink) -> TreapLink {
    match (a, b) {
        (None, b) => b,
        (a, None) => a,
        (Some(mut a), Some(mut b)) => {
            if a.priority > b.priority {
                a.right = merge_treaps(a.right.take(), Some(b));
                Some(a)
            } else {
                b.left = merge_treaps(Some(a), b.left.take());
                Some(b)
            }
        }
    }
}
fn treap_insert(root: TreapLink, key: i32, priority: u64) -> TreapLink {
    let Some(mut n) = root else {
        return Some(Box::new(TreapNode {
            key,
            priority,
            left: None,
            right: None,
        }));
    };
    if key == n.key {
        return Some(n);
    }
    if key < n.key {
        n.left = treap_insert(n.left.take(), key, priority);
        if n.left.as_ref().unwrap().priority > n.priority {
            let mut top = n.left.take().unwrap();
            n.left = top.right.take();
            top.right = Some(n);
            return Some(top);
        }
    } else {
        n.right = treap_insert(n.right.take(), key, priority);
        if n.right.as_ref().unwrap().priority > n.priority {
            let mut top = n.right.take().unwrap();
            n.right = top.left.take();
            top.left = Some(n);
            return Some(top);
        }
    }
    Some(n)
}
fn treap_delete(root: TreapLink, key: i32) -> TreapLink {
    let Some(mut n) = root else {
        return None;
    };
    if key == n.key {
        return merge_treaps(n.left.take(), n.right.take());
    }
    if key < n.key {
        n.left = treap_delete(n.left.take(), key);
    } else {
        n.right = treap_delete(n.right.take(), key);
    }
    Some(n)
}
fn treap_operations(ops: &[(bool, i32)]) -> Vec<i32> {
    let mut root = None;
    let mut random = 0xC0FFEE_u64;
    for &(insert, key) in ops {
        random ^= random << 13;
        random ^= random >> 7;
        random ^= random << 17;
        root = if insert {
            treap_insert(root, key, random)
        } else {
            treap_delete(root, key)
        };
    }
    fn walk(root: &TreapLink, out: &mut Vec<i32>) {
        if let Some(n) = root {
            walk(&n.left, out);
            out.push(n.key);
            walk(&n.right, out);
        }
    }
    let mut out = Vec::new();
    walk(&root, &mut out);
    out
}

fn main() {
    let result = csv(treap_operations(&[
        (true, 5),
        (true, 2),
        (true, 8),
        (true, 1),
        (false, 2),
    ]));
    println!("{result}");
}
