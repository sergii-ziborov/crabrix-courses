fn centroid_root(graph: &[Vec<usize>]) -> usize {
    fn collect(
        v: usize,
        p: usize,
        g: &[Vec<usize>],
        blocked: &[bool],
        sizes: &mut [usize],
        members: &mut Vec<usize>,
    ) {
        sizes[v] = 1;
        members.push(v);
        for &u in &g[v] {
            if u != p && !blocked[u] {
                collect(u, v, g, blocked, sizes, members);
                sizes[v] += sizes[u];
            }
        }
    }
    fn decompose(
        start: usize,
        parent: Option<usize>,
        g: &[Vec<usize>],
        blocked: &mut [bool],
        answer: &mut [Option<usize>],
        sizes: &mut [usize],
    ) {
        let mut members = Vec::new();
        collect(start, g.len(), g, blocked, sizes, &mut members);
        let total = members.len();
        let centroid = *members
            .iter()
            .filter(|&&v| {
                let mut largest = total - sizes[v];
                for &u in &g[v] {
                    if !blocked[u] && sizes[u] < sizes[v] {
                        largest = largest.max(sizes[u]);
                    }
                }
                largest <= total / 2
            })
            .min()
            .unwrap();
        answer[centroid] = parent;
        blocked[centroid] = true;
        for &u in &g[centroid] {
            if !blocked[u] {
                decompose(u, Some(centroid), g, blocked, answer, sizes);
            }
        }
    }
    assert!(!graph.is_empty());
    let mut parents = vec![None; graph.len()];
    decompose(
        0,
        None,
        graph,
        &mut vec![false; graph.len()],
        &mut parents,
        &mut vec![0; graph.len()],
    );
    parents.iter().position(Option::is_none).unwrap()
}

fn main() {
    let result = centroid_root(&[
        vec![1],
        vec![0, 2, 3],
        vec![1],
        vec![1, 4, 5],
        vec![3],
        vec![3],
    ])
    .to_string();
    println!("{result}");
}
