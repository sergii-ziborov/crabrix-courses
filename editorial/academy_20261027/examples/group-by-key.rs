fn largest_anagram_group(words: &[&str]) -> usize {
    let mut groups = std::collections::HashMap::new();
    for word in words {
        let mut key: Vec<char> = word.chars().collect();
        key.sort_unstable();
        *groups.entry(key).or_insert(0) += 1;
    }
    groups.values().copied().max().unwrap_or(0)
}

fn main() {
    let result = largest_anagram_group(&["eat", "tea", "tan", "ate", "nat"]).to_string();
    println!("{result}");
}
