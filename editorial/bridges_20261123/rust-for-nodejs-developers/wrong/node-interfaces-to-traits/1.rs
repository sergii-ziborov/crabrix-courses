pub trait Priced {
    fn cents(&self) -> u64;
    fn label(&self) -> String;
}

pub struct Book {
    pub title: String,
    pub cents: u64,
}

pub struct Coffee {
    pub size: u32,
}

impl Priced for Book {
    fn cents(&self) -> u64 {
        self.cents
    }
    fn label(&self) -> String {
        self.title.clone()
    }
}

impl Priced for Coffee {
    fn cents(&self) -> u64 {
        250 + 50 * u64::from(self.size)
    }
    fn label(&self) -> String {
        String::from("coffee")
    }
}

pub fn total<T: Priced>(items: &[T]) -> u64 {
    items.iter().map(|item| item.cents()).sum()
}

pub fn cheapest(items: &[Box<dyn Priced>]) -> Option<String> {
    let mut best: Option<&Box<dyn Priced>> = None;
    for item in items {
        if best.map_or(true, |b| item.cents() <= b.cents()) {
            best = Some(item);
        }
    }
    best.map(|item| item.label())
}
