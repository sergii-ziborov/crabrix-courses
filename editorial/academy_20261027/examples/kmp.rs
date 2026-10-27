fn kmp_first(text: &str, pattern: &str) -> i32 {
    let (a, p) = (text.as_bytes(), pattern.as_bytes());
    if p.is_empty() {
        return 0;
    }
    let mut prefix = vec![0; p.len()];
    for i in 1..p.len() {
        let mut j = prefix[i - 1];
        while j > 0 && p[i] != p[j] {
            j = prefix[j - 1];
        }
        if p[i] == p[j] {
            j += 1;
        }
        prefix[i] = j;
    }
    let mut matched = 0;
    for (i, &c) in a.iter().enumerate() {
        while matched > 0 && c != p[matched] {
            matched = prefix[matched - 1];
        }
        if c == p[matched] {
            matched += 1;
        }
        if matched == p.len() {
            return (i + 1 - p.len()) as i32;
        }
    }
    -1 // byte offset; exercises use ASCII
}

fn main() {
    let result = kmp_first("ababcabcabababd", "ababd").to_string();
    println!("{result}");
}
