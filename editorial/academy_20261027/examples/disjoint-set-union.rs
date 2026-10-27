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
fn components_after_unions(n: usize, unions: &[(usize, usize)]) -> usize {
    let mut sets = Dsu::new(n);
    for &(a, b) in unions {
        sets.join(a, b);
    }
    sets.count
}

fn main() {
    let result = components_after_unions(5, &[(0, 1), (1, 2), (3, 4)]).to_string();
    println!("{result}");
}
