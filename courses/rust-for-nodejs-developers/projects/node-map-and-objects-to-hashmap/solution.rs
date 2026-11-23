// JavaScript original:
// function totalsByCustomer(orders) {
//   const totals = new Map();
//   for (const [customer, cents] of orders) {
//     totals.set(customer, (totals.get(customer) ?? 0) + cents);
//   }
//   return totals;
// }
use std::collections::HashMap;

pub fn totals_by_customer(orders: &[(&str, u64)]) -> HashMap<String, u64> {
    todo!("implement the contract")
}
