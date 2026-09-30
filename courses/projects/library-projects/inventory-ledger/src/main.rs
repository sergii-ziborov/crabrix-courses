use std::collections::BTreeMap;

enum Transaction {
    Receive(&'static str, i32),
    Sell(&'static str, i32),
}

fn apply(
    stock: &mut BTreeMap<&'static str, i32>,
    transaction: Transaction,
) {
    let (item, change) = match transaction {
        Transaction::Receive(item, count) => (item, count),
        Transaction::Sell(item, count) => (item, -count),
    };
    *stock.entry(item).or_insert(0) += change;
}

fn main() {
    let mut stock = BTreeMap::new();
    for transaction in [
        Transaction::Receive("keyboard", 12),
        Transaction::Receive("mouse", 20),
        Transaction::Sell("keyboard", 3),
    ] {
        apply(&mut stock, transaction);
    }
    for (item, count) in stock {
        println!("{item:<10} {count:>3}");
    }
}