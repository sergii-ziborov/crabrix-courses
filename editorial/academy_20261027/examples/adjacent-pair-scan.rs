fn decreases(values: &[i32]) -> usize {
    values.windows(2).filter(|pair| pair[1] < pair[0]).count()
}

fn main() {
    let result = decreases(&[3,5,4,4,1]).to_string();
    println!("{result}");
}
