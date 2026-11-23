pub fn first_price_over(items: &[u32], limit: u32, mut price_of: impl FnMut(u32) -> u32) -> Option<u32> {
    let prices: Vec<u32> = items.iter().map(|&item| price_of(item)).collect();
    prices.into_iter().find(|&price| price > limit)
}
