fn arrows(intervals: &[(i32, i32)]) -> usize {
    let mut sorted = intervals.to_vec();
    sorted.sort_by_key(|&(a, b)| (b, a));
    let mut last = None;
    let mut count = 0;
    for (start, end) in sorted {
        if last.is_none_or(|x| start > x) {
            count += 1;
            last = Some(end);
        }
    }
    count
}

fn main() {
    let result = arrows(&[(10, 16), (2, 8), (1, 6), (7, 12)]).to_string();
    println!("{result}");
}
