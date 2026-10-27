fn rooms(intervals: &[(i32, i32)]) -> usize {
    let mut sorted = intervals.to_vec();
    sorted.sort_unstable();
    let mut ends = std::collections::BinaryHeap::new();
    let mut best = 0;
    for (start, end) in sorted {
        while ends.peek().is_some_and(|&std::cmp::Reverse(e)| e <= start) {
            ends.pop();
        }
        ends.push(std::cmp::Reverse(end));
        best = best.max(ends.len());
    }
    best
}

fn main() {
    let result = rooms(&[(0, 30), (5, 10), (15, 20)]).to_string();
    println!("{result}");
}
