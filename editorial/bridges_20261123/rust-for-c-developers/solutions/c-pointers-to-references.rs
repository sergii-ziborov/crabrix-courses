pub fn append_doubled(dst: &mut Vec<i32>, src: &[i32]) {
    for &x in src {
        dst.push(2 * x);
    }
}
