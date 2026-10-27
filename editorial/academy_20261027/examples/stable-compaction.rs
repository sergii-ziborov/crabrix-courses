fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn compact_nonzero(values: &mut Vec<i32>) {
    let mut write = 0;
    for read in 0..values.len() {
        if values[read] != 0 { values[write] = values[read]; write += 1; }
    }
    values.truncate(write);
}

fn main() {
    let result = { let mut values=vec![0,4,0,2,7,0]; compact_nonzero(&mut values); csv(values) };
    println!("{result}");
}
