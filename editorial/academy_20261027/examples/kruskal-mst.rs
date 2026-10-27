struct Dsu {
    parent: Vec<usize>,
    size: Vec<usize>,
    count: usize,
}
impl Dsu {
    fn new(n: usize) -> Self {
        Self {
            parent: (0..n).collect(),
            size: vec![1; n],
            count: n,
        }
    }
    fn root(&mut self, mut x: usize) -> usize {
        while x != self.parent[x] {
            self.parent[x] = self.parent[self.parent[x]];
            x = self.parent[x];
        }
        x
    }
    fn join(&mut self, a: usize, b: usize) -> bool {
        let (mut a, mut b) = (self.root(a), self.root(b));
        if a == b {
            return false;
        }
        if self.size[a] < self.size[b] {
            std::mem::swap(&mut a, &mut b);
        }
        self.parent[b] = a;
        self.size[a] += self.size[b];
        self.count -= 1;
        true
    }
}
fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
fn kruskal_weights(n: usize, edges: &[(usize, usize, i64)]) -> Vec<i64> {
    let mut sorted = edges.to_vec();
    sorted.sort_by_key(|&(a, b, w)| (w, a, b));
    let mut dsu = Dsu::new(n);
    let mut out = Vec::new();
    for (a, b, w) in sorted {
        if dsu.join(a, b) {
            out.push(w);
        }
    }
    assert!(n == 0 || out.len() == n - 1, "connected graph required");
    out
}

fn main() {
    let result = csv(kruskal_weights(
        4,
        &[(0, 1, 1), (0, 2, 4), (1, 2, 2), (1, 3, 5), (2, 3, 3)],
    ));
    println!("{result}");
}
