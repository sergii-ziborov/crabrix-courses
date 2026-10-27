fn stack_min(operations:&[&str])->i32 {
    let mut stack:Vec<(i32,i32)>=Vec::new();
    for op in operations {
        if let Some(value)=op.strip_prefix("push") {
            let x=value.parse().unwrap(); let minimum=stack.last().map_or(x,|&(_,m)|m.min(x)); stack.push((x,minimum));
        } else if *op=="pop" { stack.pop().unwrap(); }
    }
    stack.last().unwrap().1
}

fn main() {
    let result = stack_min(&["push5","push2","push4","pop","min"]).to_string();
    println!("{result}");
}
