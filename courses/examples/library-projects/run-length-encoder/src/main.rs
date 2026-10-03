fn encode(input: &str) -> String {
    let mut out = String::new();
    let mut chars = input.chars().peekable();

    while let Some(current) = chars.next() {
        let mut run = 1;
        while chars.peek() == Some(&current) {
            chars.next();
            run += 1;
        }
        out.push_str(&run.to_string());
        out.push(current);
    }
    out
}

fn decode(input: &str) -> String {
    let mut out = String::new();
    let mut count = String::new();

    for character in input.chars() {
        if character.is_ascii_digit() {
            count.push(character);
        } else {
            let run: usize = count.parse().unwrap_or(1);
            out.push_str(&character.to_string().repeat(run));
            count.clear();
        }
    }
    out
}

fn main() {
    let original = "aaabccddddde";
    let packed = encode(original);
    let restored = decode(&packed);

    println!("original  {original}");
    println!("encoded   {packed}");
    println!("decoded   {restored}");
    assert_eq!(original, restored);
    println!("round trip verified");
}