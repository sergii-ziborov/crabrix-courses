#[derive(Clone)]
struct SuffixState {
    length: usize,
    link: Option<usize>,
    next: std::collections::BTreeMap<u8, usize>,
}
fn distinct_substrings(text: &str) -> usize {
    let empty = SuffixState {
        length: 0,
        link: None,
        next: std::collections::BTreeMap::new(),
    };
    let mut states = vec![empty.clone()];
    let mut last = 0;
    for c in text.bytes() {
        let current = states.len();
        states.push(SuffixState {
            length: states[last].length + 1,
            ..empty.clone()
        });
        let mut p = Some(last);
        while let Some(v) = p {
            if states[v].next.contains_key(&c) {
                break;
            }
            states[v].next.insert(c, current);
            p = states[v].link;
        }
        if let Some(v) = p {
            let q = states[v].next[&c];
            if states[v].length + 1 == states[q].length {
                states[current].link = Some(q);
            } else {
                let clone = states.len();
                let mut copied = states[q].clone();
                copied.length = states[v].length + 1;
                states.push(copied);
                while let Some(v) = p {
                    if states[v].next.get(&c) != Some(&q) {
                        break;
                    }
                    states[v].next.insert(c, clone);
                    p = states[v].link;
                }
                states[q].link = Some(clone);
                states[current].link = Some(clone);
            }
        } else {
            states[current].link = Some(0);
        }
        last = current;
    }
    states
        .iter()
        .skip(1)
        .map(|s| s.length - states[s.link.unwrap()].length)
        .sum()
}

fn main() {
    let result = distinct_substrings("ababa").to_string();
    println!("{result}");
}
