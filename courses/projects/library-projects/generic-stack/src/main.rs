use std::fmt::Debug;

struct Stack<T> {
    items: Vec<T>,
}

impl<T: Debug> Stack<T> {
    fn new() -> Self {
        Stack { items: Vec::new() }
    }

    fn push(&mut self, item: T) {
        self.items.push(item);
    }

    fn pop(&mut self) -> Option<T> {
        self.items.pop()
    }

    fn peek(&self) -> Option<&T> {
        self.items.last()
    }

    fn len(&self) -> usize {
        self.items.len()
    }

    fn describe(&self, label: &str) {
        println!("{label:<10} len={} top={:?}", self.len(), self.peek());
    }
}

fn main() {
    let mut numbers: Stack<i32> = Stack::new();
    for value in [3, 1, 4, 1, 5] {
        numbers.push(value);
    }
    numbers.describe("numbers");

    let mut words: Stack<&str> = Stack::new();
    for word in ["rust", "is", "explicit"] {
        words.push(word);
    }
    words.describe("words");

    while let Some(word) = words.pop() {
        println!("popped {word}");
    }
    words.describe("drained");
}