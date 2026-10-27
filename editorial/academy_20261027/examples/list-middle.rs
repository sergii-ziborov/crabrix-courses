
type Link=Option<Box<ListNode>>;
struct ListNode { value:i32, next:Link }
fn list(values:&[i32])->Link {
    values.iter().rev().fold(None,|next,&value|Some(Box::new(ListNode{value,next})))
}
fn list_values(head:&Link)->Vec<i32> {
    let mut out=Vec::new(); let mut p=head.as_deref();
    while let Some(n)=p { out.push(n.value); p=n.next.as_deref(); } out
}
fn list_middle(head:&Link)->i32 {
    let (mut slow,mut fast)=(head.as_deref(),head.as_deref());
    while let Some(next)=fast.and_then(|n|n.next.as_deref()) {
        slow=slow.unwrap().next.as_deref(); fast=next.next.as_deref();
    }
    slow.expect("nonempty list").value
}

fn main() {
    let result = list_middle(&list(&[1,2,3,4,5,6])).to_string();
    println!("{result}");
}
