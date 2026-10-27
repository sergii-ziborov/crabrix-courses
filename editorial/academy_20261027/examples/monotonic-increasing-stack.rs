fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn previous_smaller(values:&[i32])->Vec<i32> {
    let mut stack=Vec::new(); let mut result=Vec::new();
    for &x in values {
        while stack.last().is_some_and(|&old|old>=x) { stack.pop(); }
        result.push(stack.last().copied().unwrap_or(-1)); stack.push(x);
    }
    result
}

fn main() {
    let result = csv(previous_smaller(&[4,5,2,10,8]));
    println!("{result}");
}
