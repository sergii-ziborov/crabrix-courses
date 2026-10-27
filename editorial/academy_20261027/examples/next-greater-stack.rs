fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn next_greater(values:&[i32])->Vec<i32> {
    let mut result=vec![-1;values.len()]; let mut unresolved=Vec::new();
    for (i,&x) in values.iter().enumerate() {
        while unresolved.last().is_some_and(|&j|values[j]<x) { result[unresolved.pop().unwrap()]=x; }
        unresolved.push(i);
    }
    result
}

fn main() {
    let result = csv(next_greater(&[2,1,2,4,3]));
    println!("{result}");
}
