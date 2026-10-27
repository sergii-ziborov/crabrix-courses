fn follows_pattern(pattern: &str, words: &[&str]) -> bool {
    let letters: Vec<_> = pattern.chars().collect();
    if letters.len() != words.len() {
        return false;
    }
    let (mut forward, mut reverse) = (
        std::collections::HashMap::new(),
        std::collections::HashMap::new(),
    );
    for (&letter, &word) in letters.iter().zip(words) {
        if forward.get(&letter).is_some_and(|&old| old != word)
            || reverse.get(word).is_some_and(|&old| old != letter)
        {
            return false;
        }
        forward.insert(letter, word);
        reverse.insert(word, letter);
    }
    true
}

fn main() {
    let result = follows_pattern("abba", &["red", "blue", "blue", "red"]).to_string();
    println!("{result}");
}
