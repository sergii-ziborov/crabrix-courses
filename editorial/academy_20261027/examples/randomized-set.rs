fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
#[derive(Default)]
struct DenseSet { values: Vec<i32>, index: std::collections::HashMap<i32, usize> }
impl DenseSet {
    fn insert(&mut self, x: i32) {
        if self.index.contains_key(&x) { return; }
        self.index.insert(x, self.values.len()); self.values.push(x);
    }
    fn remove(&mut self, x: i32) {
        if let Some(i) = self.index.remove(&x) {
            self.values.swap_remove(i);
            if i < self.values.len() { self.index.insert(self.values[i], i); }
        }
    }
    // A caller-supplied uniform index gives a uniform stored element.
    fn sample(&self, uniform_index: usize) -> Option<i32> { self.values.get(uniform_index).copied() }
}
fn dense_operations(ops: &[(bool, i32)]) -> Vec<i32> {
    let mut set = DenseSet::default();
    for &(insert, x) in ops { if insert { set.insert(x); } else { set.remove(x); } }
    let _ = set.sample(0);
    set.values.sort_unstable(); set.values
}

fn main() {
    let result = csv(dense_operations(&[(true,4),(true,9),(false,4),(true,7)]));
    println!("{result}");
}
