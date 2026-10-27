fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn stock_spans(prices:&[i32])->Vec<usize> {
    let mut stack:Vec<(i32,usize)>=Vec::new(); let mut result=Vec::new();
    for &price in prices {
        let mut span=1; // include today
        while stack.last().is_some_and(|&(p,_)|p<=price) { span+=stack.pop().unwrap().1; }
        stack.push((price,span)); result.push(span);
    }
    result
}

fn main() {
    let result = csv(stock_spans(&[100,80,60,70,60,75,85]));
    println!("{result}");
}
