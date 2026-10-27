fn rotated_index(a: &[i32], target: i32) -> i32 {
    let (mut lo, mut hi) = (0, a.len()); // distinct values
    while lo < hi {
        let mid = lo + (hi - lo) / 2;
        if a[mid] == target {
            return mid as i32;
        }
        if a[lo] <= a[mid] {
            if a[lo] <= target && target < a[mid] {
                hi = mid;
            } else {
                lo = mid + 1;
            }
        } else if a[mid] < target && target <= a[hi - 1] {
            lo = mid + 1;
        } else {
            hi = mid;
        }
    }
    -1
}

fn main() {
    let result = rotated_index(&[4, 5, 6, 7, 0, 1, 2], 0).to_string();
    println!("{result}");
}
