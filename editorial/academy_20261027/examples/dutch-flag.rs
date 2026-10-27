fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn sort_three(values: &mut [i32]) {
    let (mut low, mut scan, mut high) = (0, 0, values.len());
    while scan < high {
        match values[scan] {
            0 => {
                values.swap(low, scan);
                low += 1;
                scan += 1;
            }
            1 => scan += 1,
            2 => {
                high -= 1;
                values.swap(scan, high);
            }
            _ => panic!("only 0, 1 and 2 are allowed"),
        }
    }
}

fn main() {
    let result = {
        let mut values = vec![2, 0, 2, 1, 1, 0];
        sort_three(&mut values);
        csv(values)
    };
    println!("{result}");
}
