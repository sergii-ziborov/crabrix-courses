fn matrix_contains(a: &[Vec<i32>], target: i32) -> bool {
    if a.is_empty() || a[0].is_empty() {
        return false;
    }
    let cols = a[0].len();
    let (mut lo, mut hi) = (0, a.len() * cols);
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        let value = a[mid / cols][mid % cols];
        if value == target {
            return true;
        }
        if value < target {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    false // Row-major ordering must be globally sorted.
}

fn main() {
    let result = matrix_contains(
        &[vec![1, 3, 5, 7], vec![10, 11, 16, 20], vec![23, 30, 34, 60]],
        16,
    )
    .to_string();
    println!("{result}");
}
