fn maximum_meetings(intervals: &[(i32, i32)]) -> usize {
    let mut sorted = intervals.to_vec();
    sorted.sort_by_key(|&(s, e)| (e, s));
    let mut end = i32::MIN;
    let mut kept = 0;
    for (s, e) in sorted {
        if s >= end {
            kept += 1;
            end = e;
        }
    }
    kept
}

fn main() {
    let result = maximum_meetings(&[(1, 2), (3, 4), (0, 6), (5, 7), (8, 9), (5, 9)]).to_string();
    println!("{result}");
}
