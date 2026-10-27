fn queue_front(operations:&[&str])->i32 {
    let (mut incoming,mut outgoing)=(Vec::new(),Vec::new());
    for op in operations {
        if let Some(value)=op.strip_prefix("enqueue") { incoming.push(value.parse::<i32>().unwrap()); continue; }
        if outgoing.is_empty() { while let Some(x)=incoming.pop() { outgoing.push(x); } }
        if *op=="dequeue" { outgoing.pop().unwrap(); }
    }
    *outgoing.last().unwrap()
}

fn main() {
    let result = queue_front(&["enqueue3","enqueue5","enqueue8","dequeue","dequeue","enqueue2","front"]).to_string();
    println!("{result}");
}
