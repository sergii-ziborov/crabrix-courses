fn range_xor(values: &[i32], left: usize, right: usize) -> i32 {
    let mut prefix = vec![0; values.len() + 1];
    for (i, &x) in values.iter().enumerate() { prefix[i+1] = prefix[i] ^ x; }
    prefix[right + 1] ^ prefix[left]
}

fn main() {
    let result = range_xor(&[5,1,7,3,2],1,4).to_string();
    println!("{result}");
}
