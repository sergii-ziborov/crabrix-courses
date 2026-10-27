fn sorted_median(a: &[i32], b: &[i32]) -> f64 {
    if a.len() > b.len() {
        return sorted_median(b, a);
    }
    assert!(!b.is_empty());
    let half = (a.len() + b.len()).div_ceil(2);
    let (mut lo, mut hi) = (0, a.len());
    loop {
        let i = lo + (hi - lo) / 2;
        let j = half - i;
        let al = if i == 0 { i32::MIN } else { a[i - 1] };
        let ar = a.get(i).copied().unwrap_or(i32::MAX);
        let bl = if j == 0 { i32::MIN } else { b[j - 1] };
        let br = b.get(j).copied().unwrap_or(i32::MAX);
        if al <= br && bl <= ar {
            if (a.len() + b.len()) % 2 == 1 {
                return al.max(bl) as f64;
            }
            return (al.max(bl) as f64 + ar.min(br) as f64) / 2.0;
        }
        if al > br {
            hi = i - 1;
        } else {
            lo = i + 1;
        }
    }
}

fn main() {
    let result = sorted_median(&[1, 3], &[2, 4]).to_string();
    println!("{result}");
}
