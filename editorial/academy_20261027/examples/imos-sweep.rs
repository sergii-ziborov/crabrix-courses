fn peak_load(n: usize, updates: &[(usize, usize, i64)]) -> i64 {
    let mut events = vec![0; n + 1];
    for &(left, right, delta) in updates {
        events[left] += delta;
        events[right + 1] -= delta;
    }
    let (mut active, mut peak) = (0, 0);
    for &delta in &events[..n] {
        active += delta;
        peak = peak.max(active);
    }
    peak
}

fn main() {
    let result = peak_load(5, &[(0, 2, 2), (1, 3, 3), (3, 4, 1)]).to_string();
    println!("{result}");
}
