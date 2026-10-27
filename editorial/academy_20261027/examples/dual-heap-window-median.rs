fn csv<T: std::fmt::Display>(a: impl IntoIterator<Item = T>) -> String {
    a.into_iter()
        .map(|x| x.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
use std::{
    cmp::Reverse,
    collections::{BinaryHeap, HashMap},
};
#[derive(Default)]
struct MedianWindow {
    low: BinaryHeap<i32>,
    high: BinaryHeap<Reverse<i32>>,
    deleted: HashMap<i32, usize>,
    low_size: usize,
    high_size: usize,
}
impl MedianWindow {
    fn prune(&mut self) {
        while let Some(&x) = self.low.peek() {
            let count = self.deleted.get(&x).copied().unwrap_or(0);
            if count == 0 {
                break;
            }
            if count == 1 {
                self.deleted.remove(&x);
            } else {
                self.deleted.insert(x, count - 1);
            }
            self.low.pop();
        }
        while let Some(&Reverse(x)) = self.high.peek() {
            let count = self.deleted.get(&x).copied().unwrap_or(0);
            if count == 0 {
                break;
            }
            if count == 1 {
                self.deleted.remove(&x);
            } else {
                self.deleted.insert(x, count - 1);
            }
            self.high.pop();
        }
    }
    fn balance(&mut self) {
        self.prune();
        while self.low_size > self.high_size + 1 {
            let x = self.low.pop().unwrap();
            self.low_size -= 1;
            self.high_size += 1;
            self.high.push(Reverse(x));
            self.prune();
        }
        while self.low_size < self.high_size {
            let Reverse(x) = self.high.pop().unwrap();
            self.high_size -= 1;
            self.low_size += 1;
            self.low.push(x);
            self.prune();
        }
    }
    fn add(&mut self, x: i32) {
        self.prune();
        if self.low.peek().is_none_or(|&m| x <= m) {
            self.low.push(x);
            self.low_size += 1;
        } else {
            self.high.push(Reverse(x));
            self.high_size += 1;
        }
        self.balance();
    }
    fn remove(&mut self, x: i32) {
        self.prune();
        if x <= *self.low.peek().unwrap() {
            self.low_size -= 1;
        } else {
            self.high_size -= 1;
        }
        *self.deleted.entry(x).or_default() += 1;
        self.balance();
    }
}
fn sliding_medians(values: &[i32], k: usize) -> Vec<i32> {
    assert!(k > 0 && k % 2 == 1 && k <= values.len());
    let mut state = MedianWindow::default();
    let mut out = Vec::new();
    for i in 0..values.len() {
        state.add(values[i]);
        if i >= k {
            state.remove(values[i - k]);
        }
        // Lazy deletion alone can retain O(n) stale entries. Periodic rebuild
        // bounds storage by O(k), with amortised O(log k) update cost.
        if state.low.len() + state.high.len() > 4 * k {
            state = MedianWindow::default();
            for &x in &values[i + 1 - k..=i] {
                state.add(x);
            }
        }
        if i + 1 >= k {
            state.prune();
            out.push(*state.low.peek().unwrap());
        }
    }
    out
}

fn main() {
    let result = csv(sliding_medians(&[1, 3, -1, -3, 5, 3, 6, 7], 3));
    println!("{result}");
}
