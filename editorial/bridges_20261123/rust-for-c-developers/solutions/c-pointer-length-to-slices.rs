pub fn longest_run(xs: &[i32]) -> &[i32] {
    let mut best = 0..0;
    let mut start = 0;
    for i in 1..=xs.len() {
        if i == xs.len() || xs[i] != xs[start] {
            if i - start > best.len() {
                best = start..i;
            }
            start = i;
        }
    }
    &xs[best]
}
