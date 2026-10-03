fn classify(value: u32) -> String {
    match (value % 3, value % 5) {
        (0, 0) => "FizzBuzz".to_string(),
        (0, _) => "Fizz".to_string(),
        (_, 0) => "Buzz".to_string(),
        _ => value.to_string(),
    }
}

fn main() {
    for value in 1..=20 {
        println!("{:>2} -> {}", value, classify(value));
    }
}