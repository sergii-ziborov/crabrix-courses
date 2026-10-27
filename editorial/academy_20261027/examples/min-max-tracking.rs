fn spread(values: &[i32]) -> i32 {
    assert!(!values.is_empty());
    let (mut low, mut high) = (values[0], values[0]);
    for &x in &values[1..] {
        low = low.min(x);
        high = high.max(x);
    }
    high - low
}

fn main() {
    let result = spread(&[8, 3, 11, 6]).to_string();
    println!("{result}");
}
