fn has_cycle(graph: &[Vec<usize>]) -> bool {
    fn visit(v: usize, parent: usize, g: &[Vec<usize>], seen: &mut [bool]) -> bool {
        seen[v] = true;
        for &u in &g[v] {
            if u != parent && (seen[u] || visit(u, v, g, seen)) {
                return true;
            }
        }
        false
    }
    // Simple undirected graph: parallel edges require edge IDs instead.
    let mut seen = vec![false; graph.len()];
    (0..graph.len()).any(|v| !seen[v] && visit(v, graph.len(), graph, &mut seen))
}

fn main() {
    let result = has_cycle(&[vec![1, 2], vec![0, 2], vec![0, 1, 3], vec![2]]).to_string();
    println!("{result}");
}
