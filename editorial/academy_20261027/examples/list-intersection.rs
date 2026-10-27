
type SharedLink=Option<std::rc::Rc<SharedNode>>;
struct SharedNode { value:i32, next:SharedLink }
fn shared_list(prefix:&[i32],tail:SharedLink)->SharedLink {
    prefix.iter().rev().fold(tail,|next,&value|Some(std::rc::Rc::new(SharedNode{value,next})))
}
fn intersection(a:&SharedLink,b:&SharedLink)->Option<i32> {
    fn equal(a:&SharedLink,b:&SharedLink)->bool {
        match (a,b) { (None,None)=>true, (Some(x),Some(y))=>std::rc::Rc::ptr_eq(x,y), _=>false }
    }
    let (mut p,mut q)=(a.clone(),b.clone());
    while !equal(&p,&q) {
        p=match p { Some(n)=>n.next.clone(), None=>b.clone() };
        q=match q { Some(n)=>n.next.clone(), None=>a.clone() };
    }
    p.map(|n|n.value)
}

fn main() {
    let result = { let tail=shared_list(&[8,4,5],None); let a=shared_list(&[4,1],tail.clone()); let b=shared_list(&[5,6,1],tail); intersection(&a,&b).map_or("none".into(),|x|x.to_string()) };
    println!("{result}");
}
