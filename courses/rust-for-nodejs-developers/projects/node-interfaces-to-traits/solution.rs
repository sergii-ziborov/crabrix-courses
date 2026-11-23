// TypeScript original:
// interface Priced { cents(): number; label(): string }
// function total<T extends Priced>(items: T[]): number {
//   return items.reduce((sum, item) => sum + item.cents(), 0);
// }
// function cheapest(items: Priced[]): string | undefined {
//   let best: Priced | undefined;
//   for (const item of items) if (!best || item.cents() < best.cents()) best = item;
//   return best?.label();
// }
// A book costs its own price; a coffee costs 250 cents plus 50 per size step.
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
        todo!("implement the contract")
    }
    fn label(&self) -> String {
        todo!("implement the contract")
    }
}

impl Priced for Coffee {
    fn cents(&self) -> u64 {
        todo!("implement the contract")
    }
    fn label(&self) -> String {
        todo!("implement the contract")
    }
}

pub fn total<T: Priced>(items: &[T]) -> u64 {
    todo!("implement the contract")
}

pub fn cheapest(items: &[Box<dyn Priced>]) -> Option<String> {
    todo!("implement the contract")
}
