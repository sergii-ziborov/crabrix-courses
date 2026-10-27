fn greatest_container(heights: &[i32]) -> i32 {
    if heights.len() < 2 {
        return 0;
    }
    let (mut left, mut right, mut best) = (0, heights.len() - 1, 0);
    while left < right {
        best = best.max((right - left) as i32 * heights[left].min(heights[right]));
        if heights[left] <= heights[right] {
            left += 1;
        } else {
            right -= 1;
        }
    }
    best
}

fn main() {
    let result = greatest_container(&[1, 8, 6, 2, 5, 4, 8, 3, 7]).to_string();
    println!("{result}");
}
