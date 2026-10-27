fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn gray_codes(bits: usize) -> Vec<usize> {
    assert!(bits < usize::BITS as usize);
    (0..1_usize << bits).map(|i| i ^ (i >> 1)).collect()
}

fn main() {
    let result = csv(gray_codes(3));
    println!("{result}");
}
