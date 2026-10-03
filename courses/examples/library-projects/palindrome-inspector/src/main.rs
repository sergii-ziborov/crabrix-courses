fn normalized(text: &str) -> String {
    text.chars()
        .filter(|ch| ch.is_alphanumeric())
        .flat_map(char::to_lowercase)
        .collect()
}

fn is_palindrome(text: &str) -> bool {
    let clean = normalized(text);
    clean.chars().eq(clean.chars().rev())
}

fn main() {
    for phrase in [
        "Never odd or even",
        "Rust trusts rustc",
        "Was it a rat I saw?",
    ] {
        println!("{:<22} {}", phrase, is_palindrome(phrase));
    }
}