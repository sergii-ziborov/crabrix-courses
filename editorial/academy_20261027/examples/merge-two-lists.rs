
type Link=Option<Box<ListNode>>;
struct ListNode { value:i32, next:Link }
fn list(values:&[i32])->Link {
    values.iter().rev().fold(None,|next,&value|Some(Box::new(ListNode{value,next})))
}
fn list_values(head:&Link)->Vec<i32> {
    let mut out=Vec::new(); let mut p=head.as_deref();
    while let Some(n)=p { out.push(n.value); p=n.next.as_deref(); } out
}
fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn merge_lists(mut a:Link,mut b:Link)->Link {
    let mut out=None; let mut tail=&mut out;
    while a.is_some() && b.is_some() {
        let chosen=if a.as_ref().unwrap().value<=b.as_ref().unwrap().value { &mut a } else { &mut b };
        let mut node=chosen.take().unwrap(); *chosen=node.next.take();
        *tail=Some(node); tail=&mut tail.as_mut().unwrap().next;
    }
    *tail=if a.is_some() { a } else { b }; out
}

fn main() {
    let result = csv(list_values(&merge_lists(list(&[1,2,4]),list(&[1,3,4]))));
    println!("{result}");
}
