fn minimum_cover<'a>(text: &'a str, required: &str) -> &'a str {
    assert!(text.is_ascii() && required.is_ascii());
    if required.is_empty() { return ""; }
    let mut need=[0_i32;256]; for c in required.bytes() { need[c as usize]+=1; }
    let (mut missing,mut left)=(required.len(),0); let mut best=(0,usize::MAX);
    for (right,c) in text.bytes().enumerate() {
        if need[c as usize]>0 { missing-=1; } need[c as usize]-=1;
        while missing==0 {
            if right+1-left<best.1 { best=(left,right+1-left); }
            let old=text.as_bytes()[left] as usize; need[old]+=1; left+=1;
            if need[old]>0 { missing+=1; }
        }
    }
    if best.1==usize::MAX { "" } else { &text[best.0..best.0+best.1] }
}

fn main() {
    let result = minimum_cover("ADOBECODEBANC","ABC").to_string();
    println!("{result}");
}
