fn sorted_pair(values: &[i32], target: i32) -> Option<(usize, usize)> {
    if values.len() < 2 {
        return None;
    }
    let (mut left, mut right) = (0, values.len() - 1);
    while left < right {
        match (values[left] + values[right]).cmp(&target) {
            std::cmp::Ordering::Equal => return Some((left + 1, right + 1)),
            std::cmp::Ordering::Less => left += 1,
            std::cmp::Ordering::Greater => right -= 1,
        }
    }
    None
}

fn main() {
    let result =
        sorted_pair(&[2, 3, 7, 11, 15], 17).map_or("-1,-1".into(), |(a, b)| format!("{a},{b}"));
    println!("{result}");
}
