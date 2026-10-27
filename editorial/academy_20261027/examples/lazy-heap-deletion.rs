fn valid_min(ops:&[&str])->i32 {
    let mut heap=std::collections::BinaryHeap::new(); let mut deleted=std::collections::HashMap::<i32,usize>::new();
    for op in ops {
        if let Some(raw)=op.strip_prefix("push") { heap.push(std::cmp::Reverse(raw.parse::<i32>().unwrap())); }
        if let Some(raw)=op.strip_prefix("delete") { *deleted.entry(raw.parse().unwrap()).or_default()+=1; }
        while let Some(&std::cmp::Reverse(x))=heap.peek() {
            let count=deleted.entry(x).or_default(); if *count==0 { break; } *count-=1; heap.pop();
        }
    }
    heap.peek().unwrap().0
}

fn main() {
    let result = valid_min(&["push4","push7","push2","delete2","min"]).to_string();
    println!("{result}");
}
