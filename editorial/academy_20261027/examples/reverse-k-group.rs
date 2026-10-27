
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
fn reverse_groups(mut head:Link,k:usize)->Link {
    assert!(k>0); let mut result=None; let mut tail=&mut result;
    loop {
        let mut scan=head.as_deref(); let mut count=0;
        while count<k { if let Some(n)=scan { scan=n.next.as_deref(); count+=1; } else { break; } }
        if count<k { *tail=head; break; }
        let mut group=None;
        for _ in 0..k { let mut n=head.take().unwrap(); head=n.next.take(); n.next=group; group=Some(n); }
        *tail=group; for _ in 0..k { tail=&mut tail.as_mut().unwrap().next; }
    }
    result
}

fn main() {
    let result = csv(list_values(&reverse_groups(list(&[1,2,3,4,5,6,7]),3)));
    println!("{result}");
}
