fn largest_rectangle(heights:&[i32])->i32 {
    let mut stack:Vec<usize>=Vec::new(); let mut best=0;
    for i in 0..=heights.len() {
        let h=heights.get(i).copied().unwrap_or(0);
        while stack.last().is_some_and(|&j|heights[j]>h) {
            let height=heights[stack.pop().unwrap()];
            let left=stack.last().map_or(0,|&j|j+1); best=best.max(height*(i-left) as i32);
        }
        stack.push(i);
    }
    best
}

fn main() {
    let result = largest_rectangle(&[2,1,5,6,2,3]).to_string();
    println!("{result}");
}
