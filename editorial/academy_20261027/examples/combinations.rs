fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn semicolon<T: std::fmt::Display>(a: Vec<Vec<T>>) -> String {
    a.into_iter().map(csv).collect::<Vec<_>>().join(";")
}
fn combinations(values: &[i32], k: usize) -> Vec<Vec<i32>> {
    fn visit(a: &[i32], start: usize, k: usize, path: &mut Vec<i32>, out: &mut Vec<Vec<i32>>) {
        if path.len() == k {
            out.push(path.clone());
            return;
        }
        for i in start..a.len() {
            if a.len() - i < k - path.len() {
                break;
            }
            path.push(a[i]);
            visit(a, i + 1, k, path, out);
            path.pop();
        }
    }
    let mut out = Vec::new();
    visit(values, 0, k, &mut Vec::new(), &mut out);
    out
}

fn main() {
    let result = semicolon(combinations(&[1, 2, 3], 2));
    println!("{result}");
}
