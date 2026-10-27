fn lis_length(values: &[i32]) -> usize {
    let mut tails = Vec::new();
    for &x in values {
        let i = tails.partition_point(|&old| old < x);
        if i == tails.len() {
            tails.push(x);
        } else {
            tails[i] = x;
        }
    }
    tails.len()
}

fn main() {
    let result = lis_length(&[10, 9, 2, 5, 3, 7, 101, 18]).to_string();
    println!("{result}");
}
