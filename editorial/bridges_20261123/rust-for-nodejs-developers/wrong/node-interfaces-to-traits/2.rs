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

impl Coffee {
    pub fn cents(&self) -> u64 {
        250 + 50 * u64::from(self.size)
    }
    pub fn label(&self) -> String {
        String::from("coffee")
    }
}

pub fn total<T: Priced>(items: &[T]) -> u64 {
    items.iter().map(|item| item.cents()).sum()
}

pub fn cheapest(items: &[Box<dyn Priced>]) -> Option<String> {
    items.iter().min_by_key(|item| item.cents()).map(|item| item.label())
}
