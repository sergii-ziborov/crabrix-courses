fn updated_min(values: &[i32], update: (usize, i32), range: (usize, usize)) -> i32 {
    let n = values.len().next_power_of_two();
    let mut tree = vec![i32::MAX; 2 * n];
    tree[n..n + values.len()].copy_from_slice(values);
    for i in (1..n).rev() {
        tree[i] = tree[2 * i].min(tree[2 * i + 1]);
    }
    let mut i = n + update.0;
    tree[i] = update.1;
    while i > 1 {
        i /= 2;
        tree[i] = tree[2 * i].min(tree[2 * i + 1]);
    }
    let (mut left, mut right) = (range.0 + n, range.1 + n + 1);
    let mut result = i32::MAX;
    while left < right {
        if left % 2 == 1 {
            result = result.min(tree[left]);
            left += 1;
        }
        if right % 2 == 1 {
            right -= 1;
            result = result.min(tree[right]);
        }
        left /= 2;
        right /= 2;
    }
    result
}

fn main() {
    let result = updated_min(&[5, 4, 7, 2], (2, 0), (1, 3)).to_string();
    println!("{result}");
}
