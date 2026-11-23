use std::collections::HashMap;

pub fn totals_by_customer(orders: &[(&str, u64)]) -> HashMap<String, u64> {
    let mut totals: HashMap<String, u64> = HashMap::new();
    for &(customer, cents) in orders {
        let current = totals.get(customer).copied().unwrap_or(0);
        totals.insert(customer.to_string(), current + cents);
    }
    totals
}
