pub fn first_price_over(items: &[u32], limit: u32, price_of: impl FnMut(u32) -> u32) -> Option<u32> {
    items.iter().copied().map(price_of).find(|&price| price > limit)
}
