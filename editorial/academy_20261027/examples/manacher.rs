fn longest_palindrome(text: &str) -> &str {
    assert!(text.is_ascii());
    let mut symbols = vec![0_u16];
    for b in text.bytes() {
        symbols.push(b as u16 + 1);
        symbols.push(0);
    }
    let n = symbols.len();
    let mut radius = vec![0; n];
    let (mut center, mut right) = (0, 0);
    let (mut start, mut length) = (0, 0);
    for i in 0..n {
        if i < right {
            radius[i] = radius[2 * center - i].min(right - i);
        }
        while radius[i] < i
            && i + radius[i] + 1 < n
            && symbols[i - radius[i] - 1] == symbols[i + radius[i] + 1]
        {
            radius[i] += 1;
        }
        if i + radius[i] > right {
            center = i;
            right = i + radius[i];
        }
        let candidate = (i - radius[i]) / 2;
        if radius[i] > length || radius[i] == length && candidate < start {
            start = candidate;
            length = radius[i];
        }
    }
    &text[start..start + length]
}

fn main() {
    let result = longest_palindrome("babad").to_string();
    println!("{result}");
}
