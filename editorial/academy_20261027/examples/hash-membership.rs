fn has_duplicate(values: &[i32]) -> bool {
    let mut seen = std::collections::HashSet::new();
    values.iter().any(|&x| !seen.insert(x))
}

fn main() {
    let result = has_duplicate(&[11,8,3,8]).to_string();
    println!("{result}");
}
