fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn insertion_sort(values:&mut [i32]) {
    for i in 1..values.len() {
        let value=values[i]; let mut j=i;
        while j>0 && values[j-1]>value { values[j]=values[j-1]; j-=1; }
        values[j]=value;
    }
}

fn main() {
    let result = { let mut values=vec![5,2,4,6,1,3]; insertion_sort(&mut values); csv(values) };
    println!("{result}");
}
