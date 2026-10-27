fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn semicolon<T: std::fmt::Display>(a: Vec<Vec<T>>) -> String {
    a.into_iter().map(csv).collect::<Vec<_>>().join(";")
}
fn combinations_sum(candidates: &[i32], target: i32) -> Vec<Vec<i32>> {
    fn visit(a: &[i32], start: usize, left: i32, path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
        if left == 0 {
            out.push(path.clone());
            return;
        }
        for i in start..a.len() {
            if a[i] > left {
                break;
            }
            path.push(a[i]);
            visit(a, i, left - a[i], path, out);
            path.pop();
        }
    }
    let mut a = candidates.to_vec();
    assert!(a.iter().all(|&x| x > 0));
    a.sort_unstable();
    a.dedup();
    let mut out = Vec::new();
    visit(&a, 0, target, &mut Vec::new(), &mut out);
    out
}

fn main() {
    let result = semicolon(combinations_sum(&[2, 3, 6, 7], 7));
    println!("{result}");
}
