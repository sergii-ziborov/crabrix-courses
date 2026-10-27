fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn top_k(values:&[i32],k:usize)->Vec<i32> {
    let mut heap=std::collections::BinaryHeap::new();
    for &x in values { heap.push(std::cmp::Reverse(x)); if heap.len()>k { heap.pop(); } }
    let mut out:Vec<_>=heap.into_iter().map(|std::cmp::Reverse(x)|x).collect(); out.sort_unstable_by(|a,b|b.cmp(a)); out
}

fn main() {
    let result = csv(top_k(&[4,1,9,7,3,8],3));
    println!("{result}");
}
