fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn partition_lengths(text:&str)->Vec<usize> {
    assert!(text.is_ascii()); let mut last=[0;256]; for (i,c) in text.bytes().enumerate() { last[c as usize]=i; }
    let (mut start,mut end)=(0,0); let mut out=Vec::new();
    for (i,c) in text.bytes().enumerate() { end=end.max(last[c as usize]); if i==end { out.push(i+1-start); start=i+1; } } out
}

fn main() {
    let result = csv(partition_lengths("ababcbacadefegdehijhklij"));
    println!("{result}");
}
