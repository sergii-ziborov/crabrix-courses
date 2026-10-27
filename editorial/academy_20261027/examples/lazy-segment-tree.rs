struct LazySum {
    sum: Vec<i64>,
    lazy: Vec<i64>,
    n: usize,
}
impl LazySum {
    fn new(values: &[i64]) -> Self {
        let n = values.len();
        assert!(n > 0);
        let mut tree = Self {
            sum: vec![0; 4 * n],
            lazy: vec![0; 4 * n],
            n,
        };
        fn build(t: &mut LazySum, v: usize, left: usize, right: usize, a: &[i64]) {
            if right - left == 1 {
                t.sum[v] = a[left];
            } else {
                let mid = (left + right) / 2;
                build(t, v * 2, left, mid, a);
                build(t, v * 2 + 1, mid, right, a);
                t.sum[v] = t.sum[v * 2] + t.sum[v * 2 + 1];
            }
        }
        build(&mut tree, 1, 0, n, values);
        tree
    }
    fn apply(&mut self, v: usize, length: usize, delta: i64) {
        self.sum[v] += delta * length as i64;
        self.lazy[v] += delta;
    }
    fn push(&mut self, v: usize, left: usize, right: usize) {
        if right - left > 1 {
            let mid = (left + right) / 2;
            let d = self.lazy[v];
            self.apply(v * 2, mid - left, d);
            self.apply(v * 2 + 1, right - mid, d);
        }
        self.lazy[v] = 0;
    }
    fn update(&mut self, v: usize, left: usize, right: usize, from: usize, to: usize, delta: i64) {
        if to <= left || right <= from {
            return;
        }
        if from <= left && right <= to {
            self.apply(v, right - left, delta);
            return;
        }
        self.push(v, left, right);
        let mid = (left + right) / 2;
        self.update(v * 2, left, mid, from, to, delta);
        self.update(v * 2 + 1, mid, right, from, to, delta);
        self.sum[v] = self.sum[v * 2] + self.sum[v * 2 + 1];
    }
    fn query(&mut self, v: usize, left: usize, right: usize, from: usize, to: usize) -> i64 {
        if to <= left || right <= from {
            return 0;
        }
        if from <= left && right <= to {
            return self.sum[v];
        }
        self.push(v, left, right);
        let mid = (left + right) / 2;
        self.query(v * 2, left, mid, from, to) + self.query(v * 2 + 1, mid, right, from, to)
    }
    fn add(&mut self, left: usize, right: usize, delta: i64) {
        self.update(1, 0, self.n, left, right + 1, delta);
    }
    fn range_sum(&mut self, left: usize, right: usize) -> i64 {
        self.query(1, 0, self.n, left, right + 1)
    }
}
fn lazy_example(values: &[i64]) -> i64 {
    let mut tree = LazySum::new(values);
    tree.add(1, 4, 3);
    tree.range_sum(2, 5)
}

fn main() {
    let result = lazy_example(&[1, 2, 3, 4, 5, 6]).to_string();
    println!("{result}");
}
