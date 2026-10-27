fn nearest_repeat(values: &[i32]) -> Option<usize> {
    let mut last = std::collections::HashMap::new();
    let mut best = None;
    for (i, &x) in values.iter().enumerate() {
        if let Some(j) = last.insert(x, i) {
            best = Some(best.map_or(i - j, |old: usize| old.min(i - j)));
        }
    }
    best
}

fn main() {
    let result = nearest_repeat(&[5, 1, 9, 5, 1]).map_or("-1".into(), |i| i.to_string());
    println!("{result}");
}
