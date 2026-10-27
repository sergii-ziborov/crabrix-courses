fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn stream_medians(values:&[i32])->Vec<f64> {
    let mut low=std::collections::BinaryHeap::new(); let mut high=std::collections::BinaryHeap::new(); let mut out=Vec::new();
    for &x in values {
        if low.peek().is_none_or(|&m|x<=m) { low.push(x); } else { high.push(std::cmp::Reverse(x)); }
        if low.len()>high.len()+1 { high.push(std::cmp::Reverse(low.pop().unwrap())); }
        if high.len()>low.len() { low.push(high.pop().unwrap().0); }
        out.push(if low.len()==high.len() { (*low.peek().unwrap() as f64+high.peek().unwrap().0 as f64)/2.0 } else { *low.peek().unwrap() as f64 });
    }
    out
}

fn main() {
    let result = csv(stream_medians(&[5,2,10,4]));
    println!("{result}");
}
