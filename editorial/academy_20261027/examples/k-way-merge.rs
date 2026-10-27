fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn merge_many(lists:&[Vec<i32>])->Vec<i32> {
    let mut heap=std::collections::BinaryHeap::new(); let mut out=Vec::new();
    for (i,list) in lists.iter().enumerate() { if let Some(&x)=list.first() { heap.push(std::cmp::Reverse((x,i,0))); } }
    while let Some(std::cmp::Reverse((x,i,j)))=heap.pop() {
        out.push(x); if let Some(&next)=lists[i].get(j+1) { heap.push(std::cmp::Reverse((next,i,j+1))); }
    }
    out
}

fn main() {
    let result = csv(merge_many(&[vec![1,4,7],vec![2,5,8],vec![0,6,9]]));
    println!("{result}");
}
