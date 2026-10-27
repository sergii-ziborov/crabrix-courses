fn ascii_palindrome(text: &str) -> bool {
    assert!(text.is_ascii());
    let bytes = text.as_bytes();
    let (mut left, mut right) = (0, bytes.len());
    while left < right {
        if !bytes[left].is_ascii_alphanumeric() {
            left += 1;
            continue;
        }
        if !bytes[right - 1].is_ascii_alphanumeric() {
            right -= 1;
            continue;
        }
        if !bytes[left].eq_ignore_ascii_case(&bytes[right - 1]) {
            return false;
        }
        left += 1;
        right -= 1;
    }
    true
}

fn main() {
    let result = ascii_palindrome("Never odd or even").to_string();
    println!("{result}");
}
