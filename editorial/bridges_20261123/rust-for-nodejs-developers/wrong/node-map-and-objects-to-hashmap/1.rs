use std::collections::HashMap;

pub fn totals_by_customer(orders: &[(&str, u64)]) -> HashMap<String, u64> {
    let mut totals = HashMap::new();
    for &(customer, cents) in orders {
        totals.entry(customer.to_string()).or_insert(0);
        totals.insert(customer.to_string(), cents);
    }
    totals
}
