
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
fn remove_from_end(mut head:Link,n:usize)->Link {
    let mut length:usize=0; let mut scan=head.as_deref();
    while let Some(node)=scan { length+=1; scan=node.next.as_deref(); }
    assert!(n>0 && n<=length); let mut link=&mut head;
    for _ in 0..length-n { link=&mut link.as_mut().unwrap().next; }
    let next=link.as_mut().unwrap().next.take(); *link=next; head
}

fn main() {
    let result = csv(list_values(&remove_from_end(list(&[1,2,3,4,5]),2)));
    println!("{result}");
}
