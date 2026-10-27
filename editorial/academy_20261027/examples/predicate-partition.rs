fn partition_even(values: &mut [i32]) -> usize {
    let mut boundary = 0;
    for i in 0..values.len() {
        if values[i] % 2 == 0 {
            values.swap(boundary, i);
            boundary += 1;
        }
    }
    boundary
}

fn main() {
    let result = {
        let mut values = vec![5, 2, 8, 1, 4];
        partition_even(&mut values).to_string()
    };
    println!("{result}");
}
