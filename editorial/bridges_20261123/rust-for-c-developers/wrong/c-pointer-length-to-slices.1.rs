pub fn longest_run(xs: &[i32]) -> &[i32] {
    let (mut best_start, mut best_len, mut start) = (0, 0, 0);
    for i in 1..xs.len() {
        if xs[i] != xs[start] {
            if i - start > best_len {
                best_start = start;
                best_len = i - start;
            }
            start = i;
        }
    }
    &xs[best_start..best_start + best_len]
}
