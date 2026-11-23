// JavaScript original:
// function firstPriceOver(items, limit, priceOf) {
//   return items.map(priceOf).find((p) => p > limit);
// }
// Array.prototype.map calls priceOf for every item before find runs.
// Keep the Rust version lazy: stop calling price_of after the first match.
pub fn first_price_over(items: &[u32], limit: u32, price_of: impl FnMut(u32) -> u32) -> Option<u32> {
    todo!("implement the contract")
}
