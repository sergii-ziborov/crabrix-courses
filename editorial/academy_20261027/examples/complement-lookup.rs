fn two_sum(values: &[i32], target: i32) -> Option<(usize, usize)> {
    let mut seen = std::collections::HashMap::new();
    for (j, &x) in values.iter().enumerate() {
        if let Some(&i) = seen.get(&(target - x)) { return Some((i, j)); }
        seen.entry(x).or_insert(j);
    }
    None
}

fn main() {
    let result = two_sum(&[6,4,9,7],13).map_or("-1,-1".into(),|(i,j)|format!("{i},{j}"));
    println!("{result}");
}
