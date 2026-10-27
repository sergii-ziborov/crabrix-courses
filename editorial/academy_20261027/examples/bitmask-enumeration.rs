fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn matching_masks(values:&[i32],target:i32)->Vec<usize> {
    assert!(values.len()<usize::BITS as usize);
    (0..1_usize<<values.len()).filter(|&mask|values.iter().enumerate().filter(|(i,_)|mask>>i&1==1).map(|(_,x)|x).sum::<i32>()==target).collect()
}

fn main() {
    let result = csv(matching_masks(&[1,2,4],5));
    println!("{result}");
}
