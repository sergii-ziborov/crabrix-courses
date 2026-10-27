type Link = Option<Box<ListNode>>;
struct ListNode {
    value: i32,
    next: Link,
}
fn list(values: &[i32]) -> Link {
    values.iter().rev().fold(None, |next, &value| {
        Some(Box::new(ListNode { value, next }))
    })
}
fn list_values(head: &Link) -> Vec<i32> {
    let mut out = Vec::new();
    let mut p = head.as_deref();
    while let Some(n) = p {
        out.push(n.value);
        p = n.next.as_deref();
    }
    out
}
fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn reverse(mut head: Link) -> Link {
    let mut reversed = None;
    while let Some(mut node) = head {
        head = node.next.take();
        node.next = reversed;
        reversed = Some(node);
    }
    reversed
}

fn main() {
    let result = csv(list_values(&reverse(list(&[1, 2, 3, 4]))));
    println!("{result}");
}
