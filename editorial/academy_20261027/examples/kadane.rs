fn maximum_subarray(values: &[i32]) -> i32 {
    assert!(!values.is_empty());
    let (mut ending, mut best) = (values[0], values[0]);
    for &x in &values[1..] {
        ending = x.max(ending + x);
        best = best.max(ending);
    }
    best
}

fn main() {
    let result = maximum_subarray(&[-2, 1, -3, 4, -1, 2, 1, -5, 4]).to_string();
    println!("{result}");
}
