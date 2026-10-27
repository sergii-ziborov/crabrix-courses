fn single_value(values: &[i32]) -> i32 {
    // Every other value occurs exactly twice.
    values.iter().fold(0, |acc, &x| acc ^ x)
}

fn main() {
    let result = single_value(&[4, 1, 2, 1, 2]).to_string();
    println!("{result}");
}
