fn longest_run(values: &[i32]) -> usize {
    let set: std::collections::HashSet<_> = values.iter().copied().collect();
    let mut best = 0;
    for &start in &set {
        if start.checked_sub(1).is_some_and(|x| set.contains(&x)) {
            continue;
        }
        let mut length = 1;
        while start
            .checked_add(length as i32)
            .is_some_and(|x| set.contains(&x))
        {
            length += 1;
        }
        best = best.max(length);
    }
    best
}

fn main() {
    let result = longest_run(&[100, 4, 200, 1, 3, 2]).to_string();
    println!("{result}");
}
