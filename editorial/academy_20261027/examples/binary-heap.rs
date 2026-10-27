fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn heap_order(values:&[i32])->Vec<i32> {
    let mut heap=std::collections::BinaryHeap::new();
    for &x in values { heap.push(std::cmp::Reverse(x)); }
    let mut out=Vec::new(); while let Some(std::cmp::Reverse(x))=heap.pop() { out.push(x); } out
}

fn main() {
    let result = csv(heap_order(&[7,2,9,4]));
    println!("{result}");
}
