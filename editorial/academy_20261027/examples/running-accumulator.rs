fn alternating_sum(values: &[i32]) -> i32 {
    let mut sum = 0;
    for (i, &x) in values.iter().enumerate() {
        sum += if i % 2 == 0 { x } else { -x };
    }
    sum
}

fn main() {
    let result = alternating_sum(&[7,2,5,1]).to_string();
    println!("{result}");
}
