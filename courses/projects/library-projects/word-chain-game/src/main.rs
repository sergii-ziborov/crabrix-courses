use std::collections::HashSet;

fn validate(words: &[&str]) -> Result<(), String> {
    let mut seen = HashSet::new();
    for word in words {
        if !seen.insert(word.to_lowercase()) {
            return Err(format!("repeated word: {word}"));
        }
    }
    for pair in words.windows(2) {
        let left = pair[0].chars().last();
        let right = pair[1].chars().next();
        if left != right {
            return Err(format!(
                "{} does not connect to {}",
                pair[0], pair[1]
            ));
        }
    }
    Ok(())
}

fn main() {
    let good = ["crab", "borrow", "rust", "trait"];
    let bad = ["rust", "trait", "thread", "rust"];
    println!("good: {:?}", validate(&good));
    println!("bad:  {:?}", validate(&bad));
}