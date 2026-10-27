fn merged_intervals(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
    let mut sorted = intervals.to_vec();
    sorted.sort_unstable();
    let mut out: Vec<(i32, i32)> = Vec::new();
    for (s, e) in sorted {
        if let Some(last) = out.last_mut() {
            if s <= last.1 {
                last.1 = last.1.max(e);
                continue;
            }
        }
        out.push((s, e));
    }
    out
}

fn main() {
    let result = merged_intervals(&[(1, 3), (2, 6), (8, 10), (9, 12)])
        .iter()
        .map(|(a, b)| format!("{a}-{b}"))
        .collect::<Vec<_>>()
        .join(",");
    println!("{result}");
}
