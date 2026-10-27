fn longest_unique(text: &str) -> usize {
    // The exercise uses ASCII; byte positions are character positions here.
    assert!(text.is_ascii());
    let mut last=[None;256]; let (mut left,mut best)=(0,0);
    for (right,c) in text.bytes().enumerate() {
        if let Some(previous)=last[c as usize] { left=left.max(previous+1); }
        last[c as usize]=Some(right); best=best.max(right-left+1);
    }
    best
}

fn main() {
    let result = longest_unique("abcabcbb").to_string();
    println!("{result}");
}
