fn zero_triples(values: &[i32]) -> usize {
    let mut a = values.to_vec();
    a.sort_unstable();
    let mut count = 0;
    for i in 0..a.len().saturating_sub(2) {
        if i > 0 && a[i] == a[i - 1] {
            continue;
        }
        let (mut left, mut right) = (i + 1, a.len() - 1);
        while left < right {
            let sum = a[i] + a[left] + a[right];
            if sum < 0 {
                left += 1;
            } else if sum > 0 {
                right -= 1;
            } else {
                count += 1;
                let x = a[left];
                let y = a[right];
                while left < right && a[left] == x {
                    left += 1;
                }
                while left < right && a[right] == y {
                    right -= 1;
                }
            }
        }
    }
    count
}

fn main() {
    let result = zero_triples(&[-1, 0, 1, 2, -1, -4]).to_string();
    println!("{result}");
}
