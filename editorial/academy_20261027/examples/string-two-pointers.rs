fn normalized_palindrome(text:&str)->bool {
    assert!(text.is_ascii());
    let mut symbols=text.bytes().filter(|c|c.is_ascii_alphanumeric()).map(|c|c.to_ascii_lowercase());
    while let Some(first)=symbols.next() { if let Some(last)=symbols.next_back() { if first!=last { return false; } } }
    true
}

fn main() {
    let result = normalized_palindrome("A man, a plan, a canal: Panama").to_string();
    println!("{result}");
}
