use std::collections::BTreeMap;

fn main() {
    let phrase = "rust makes systems fearless rust makes ideas real";
    let mut counts = BTreeMap::new();
    for word in phrase.split_whitespace() {
        *counts.entry(word).or_insert(0) += 1;
    }
    println!("WORD LAB");
    for (word, count) in counts {
        println!("{word:>9}  {}", "█".repeat(count));
    }
}