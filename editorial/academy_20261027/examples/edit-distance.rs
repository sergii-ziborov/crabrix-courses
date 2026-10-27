fn edit_distance(a:&str,b:&str)->usize {
    assert!(a.is_ascii() && b.is_ascii()); let mut dp:Vec<_>=(0..=b.len()).collect();
    for (i,x) in a.bytes().enumerate() {
        let mut next=vec![i+1];
        for (j,y) in b.bytes().enumerate() { next.push((next[j]+1).min(dp[j+1]+1).min(dp[j]+usize::from(x!=y))); } dp=next;
    } dp[b.len()]
}

fn main() {
    let result = edit_distance("horse","ros").to_string();
    println!("{result}");
}
