
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
fn partition_list(mut head:Link,pivot:i32)->Link {
    let (mut low,mut high)=(None,None); let (mut a,mut b)=(&mut low,&mut high);
    while let Some(mut node)=head {
        head=node.next.take();
        if node.value<pivot { *a=Some(node); a=&mut a.as_mut().unwrap().next; }
        else { *b=Some(node); b=&mut b.as_mut().unwrap().next; }
    }
    *a=high; low
}

fn main() {
    let result = csv(list_values(&partition_list(list(&[1,4,3,2,5,2]),3)));
    println!("{result}");
}
