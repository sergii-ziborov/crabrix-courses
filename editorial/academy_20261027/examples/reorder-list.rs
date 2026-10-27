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
fn reorder(mut head: Link) -> Link {
    let mut length: usize = 0;
    let mut scan = head.as_deref();
    while let Some(n) = scan {
        length += 1;
        scan = n.next.as_deref();
    }
    if length < 3 {
        return head;
    }
    let mut cut = &mut head;
    for _ in 0..length.div_ceil(2) {
        cut = &mut cut.as_mut().unwrap().next;
    }
    let mut rest = cut.take();
    let mut reversed = None;
    while let Some(mut n) = rest {
        rest = n.next.take();
        n.next = reversed;
        reversed = Some(n);
    }
    let mut cursor = &mut head;
    while let Some(mut n) = reversed {
        reversed = n.next.take();
        let old = cursor.as_mut().unwrap().next.take();
        n.next = old;
        cursor.as_mut().unwrap().next = Some(n);
        cursor = &mut cursor.as_mut().unwrap().next.as_mut().unwrap().next;
    }
    head
}

fn main() {
    let result = csv(list_values(&reorder(list(&[1, 2, 3, 4, 5]))));
    println!("{result}");
}
