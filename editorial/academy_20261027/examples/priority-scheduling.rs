fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn completion_order(jobs: &[(usize, i32, i32)]) -> Vec<usize> {
    let mut arrivals = jobs.to_vec();
    arrivals.sort_by_key(|&(id, t, _)| (t, id));
    let mut ready = std::collections::BinaryHeap::new();
    let (mut i, mut time) = (0, 0);
    let mut out = Vec::new();
    while i < arrivals.len() || !ready.is_empty() {
        if ready.is_empty() {
            time = time.max(arrivals[i].1);
        }
        while i < arrivals.len() && arrivals[i].1 <= time {
            let (id, _, duration) = arrivals[i];
            ready.push(std::cmp::Reverse((duration, id)));
            i += 1;
        }
        let std::cmp::Reverse((duration, id)) = ready.pop().unwrap();
        time += duration;
        out.push(id);
    }
    out
}

fn main() {
    let result = csv(completion_order(&[(0, 0, 3), (1, 1, 1), (2, 1, 2)]));
    println!("{result}");
}
