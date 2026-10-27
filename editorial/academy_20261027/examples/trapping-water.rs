fn trapped(heights: &[i32]) -> i32 {
    let (mut left,mut right)=(0,heights.len());
    let (mut left_max,mut right_max,mut water)=(0,0,0);
    while left<right {
        if left_max<=right_max {
            left_max=left_max.max(heights[left]); water+=left_max-heights[left]; left+=1;
        } else {
            right-=1; right_max=right_max.max(heights[right]); water+=right_max-heights[right];
        }
    }
    water
}

fn main() {
    let result = trapped(&[0,1,0,2,1,0,1,3,2,1,2,1]).to_string();
    println!("{result}");
}
