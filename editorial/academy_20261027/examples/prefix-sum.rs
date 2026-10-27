fn range_sum(values: &[i64], left: usize, right: usize) -> i64 {
    let mut prefix = vec![0; values.len() + 1];
    for (i, &x) in values.iter().enumerate() {
        prefix[i + 1] = prefix[i] + x;
    }
    prefix[right + 1] - prefix[left] // inclusive [left, right]
}

fn main() {
    let result = range_sum(&[5, 2, 7, 1, 4], 1, 3).to_string();
    println!("{result}");
}
