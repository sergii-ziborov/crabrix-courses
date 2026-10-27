fn equilibrium(values: &[i32]) -> i32 {
    let total: i32 = values.iter().sum();
    let mut left = 0;
    for (i, &x) in values.iter().enumerate() {
        if left == total - left - x {
            return i as i32;
        }
        left += x;
    }
    -1
}

fn main() {
    let result = equilibrium(&[1, 7, 3, 6, 5, 6]).to_string();
    println!("{result}");
}
