fn word_break(text:&str,words:&[&str])->bool {
    assert!(text.is_ascii()); let mut possible=vec![false;text.len()+1]; possible[0]=true;
    for end in 1..=text.len() {
        possible[end]=words.iter().any(|word|word.len()<=end && possible[end-word.len()] && &text[end-word.len()..end]==*word);
    } possible[text.len()]
}

fn main() {
    let result = word_break("leetcode",&["leet","code"]).to_string();
    println!("{result}");
}
