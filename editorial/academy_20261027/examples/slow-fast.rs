fn middle_value(values: &[i32]) -> i32 {
    assert!(!values.is_empty());
    let (mut slow, mut fast) = (0, 0);
    while fast+1 < values.len() { slow += 1; fast += 2; }
    values[slow] // second middle for an even-length sequence
}

fn main() {
    let result = middle_value(&[4,8,15,16,23,42]).to_string();
    println!("{result}");
}
