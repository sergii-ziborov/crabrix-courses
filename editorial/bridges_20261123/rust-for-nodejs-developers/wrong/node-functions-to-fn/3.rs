pub fn discounted(price_cents: u64, percent: u64) -> u64 {
    if percent > 100 {
        return 0;
    }
    price_cents - price_cents * percent / 100
}

pub fn discounted_default(price_cents: u64) -> u64 {
    discounted(price_cents, 0)
}
