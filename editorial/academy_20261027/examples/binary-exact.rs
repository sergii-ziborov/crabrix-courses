fn exact_index(values: &[i32], target: i32) -> i32 {
    let (mut lo, mut hi) = (0, values.len());
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if values[mid] < target {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    if values.get(lo) == Some(&target) {
        lo as i32
    } else {
        -1
    }
}

fn main() {
    let result = exact_index(&[-1, 0, 3, 5, 9, 12], 9).to_string();
    println!("{result}");
}
