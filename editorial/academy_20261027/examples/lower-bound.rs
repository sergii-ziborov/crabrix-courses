fn lower_bound(a: &[i32], target: i32) -> usize {
    let (mut lo, mut hi) = (0, a.len());
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if a[mid] < target {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    lo
}

fn main() {
    let result = lower_bound(&[1, 2, 4, 4, 7], 4).to_string();
    println!("{result}");
}
