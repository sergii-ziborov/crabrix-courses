fn first_negative(values: &[i32]) -> i32 {
    for (i, &value) in values.iter().enumerate() {
        if value < 0 { return i as i32; }
    }
    -1
}

fn main() {
    let result = first_negative(&[4,9,-2,7]).to_string();
    println!("{result}");
}
