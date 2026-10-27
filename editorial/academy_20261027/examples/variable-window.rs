fn shortest_sum(values: &[i32], target: i32) -> usize {
    assert!(values.iter().all(|&x| x > 0));
    let (mut left, mut sum, mut best) = (0, 0, usize::MAX);
    for (right, &x) in values.iter().enumerate() {
        sum += x;
        while sum >= target {
            best = best.min(right - left + 1);
            sum -= values[left];
            left += 1;
        }
    }
    if best == usize::MAX { 0 } else { best }
}

fn main() {
    let result = shortest_sum(&[2, 3, 1, 2, 4, 3], 7).to_string();
    println!("{result}");
}
