fn pair_exists(values: &[i32], target: i32) -> bool {
    if values.len() < 2 {
        return false;
    }
    let (mut left, mut right) = (0, values.len() - 1);
    while left < right {
        let sum = values[left] + values[right];
        if sum == target {
            return true;
        }
        if sum < target {
            left += 1;
        } else {
            right -= 1;
        }
    }
    false
}

fn main() {
    let result = pair_exists(&[1, 2, 4, 6, 9], 10).to_string();
    println!("{result}");
}
