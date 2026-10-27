fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn dfs_topological(graph: &[Vec<usize>]) -> Vec<usize> {
    fn visit(v: usize, g: &[Vec<usize>], color: &mut [u8], out: &mut Vec<usize>) {
        assert_ne!(color[v], 1, "cycle");
        if color[v] == 2 {
            return;
        }
        color[v] = 1;
        for &u in &g[v] {
            visit(u, g, color, out);
        }
        color[v] = 2;
        out.push(v);
    }
    let mut sorted = graph.to_vec();
    for ns in &mut sorted {
        ns.sort_unstable();
    }
    let mut color = vec![0; graph.len()];
    let mut out = Vec::new();
    for v in 0..graph.len() {
        if color[v] == 0 {
            visit(v, &sorted, &mut color, &mut out);
        }
    }
    out.reverse();
    out
}

fn main() {
    let result = csv(dfs_topological(&[vec![2], vec![2], vec![3], vec![]]));
    println!("{result}");
}
