fn decodings(text:&str)->u64 {
    assert!(text.bytes().all(|c|c.is_ascii_digit())); let a=text.as_bytes(); let (mut before,mut current)=(1,1);
    for i in 0..a.len() {
        let mut next=if a[i]!=b'0' { current } else { 0 };
        if i>0 && (a[i-1]==b'1' || a[i-1]==b'2' && a[i]<=b'6') { next+=before; }
        before=current; current=next;
    } current
}

fn main() {
    let result = decodings("226").to_string();
    println!("{result}");
}
