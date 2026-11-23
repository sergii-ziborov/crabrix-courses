pub fn rename_all(names: &mut [String], from: &str, to: &str) -> usize {
    let mut copy = names.to_vec();
    let mut changed = 0;
    for name in copy.iter_mut() {
        if name == from {
            *name = to.to_string();
            changed += 1;
        }
    }
    changed
}

pub fn count_matches(names: &[String], wanted: &str) -> usize {
    names.iter().filter(|name| *name == wanted).count()
}
