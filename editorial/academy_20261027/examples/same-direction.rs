fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn keep_at_least(values: &mut Vec<i32>, threshold: i32) {
    let mut write = 0;
    for read in 0..values.len() {
        if values[read] >= threshold {
            values[write] = values[read];
            write += 1;
        }
    }
    values.truncate(write);
}

fn main() {
    let result = {
        let mut values = vec![7, 2, 5, 4, 9];
        keep_at_least(&mut values, 5);
        csv(values)
    };
    println!("{result}");
}
