fn peak_index(a: &[i32]) -> usize {
    assert!(!a.is_empty());
    let (mut lo, mut hi) = (0, a.len() - 1);
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if a[mid] < a[mid + 1] {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    lo // Adjacent values differ; outside endpoints are negative infinity.
}

fn main() {
    let result = peak_index(&[1, 2, 3, 1]).to_string();
    println!("{result}");
}
