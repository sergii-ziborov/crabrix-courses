pub fn append_doubled(dst: &mut Vec<i32>, src: &[i32]) {
    let start = dst.len();
    dst.reserve(src.len());
    for (i, &x) in src.iter().enumerate() {
        dst[start + i] = 2 * x;
    }
}
