fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn circular_greater(values:&[i32])->Vec<i32> {
    let n=values.len(); let mut out=vec![-1;n]; let mut stack=Vec::new();
    for step in 0..2*n {
        let i=step%n;
        while stack.last().is_some_and(|&j|values[j]<values[i]) { out[stack.pop().unwrap()]=values[i]; }
        if step<n { stack.push(i); }
    }
    out
}

fn main() {
    let result = csv(circular_greater(&[1,2,1]));
    println!("{result}");
}
