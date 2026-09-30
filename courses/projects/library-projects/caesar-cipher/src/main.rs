fn shift(character: char, amount: u8) -> char {
    if !character.is_ascii_lowercase() {
        return character;
    }
    let offset = character as u8 - b'a';
    (b'a' + (offset + amount) % 26) as char
}

fn encode(text: &str, amount: u8) -> String {
    text.chars()
        .map(|character| shift(character, amount))
        .collect()
}

fn main() {
    let message = "rust makes ownership visible";
    let encoded = encode(message, 5);
    println!("plain   {message}");
    println!("cipher  {encoded}");
}