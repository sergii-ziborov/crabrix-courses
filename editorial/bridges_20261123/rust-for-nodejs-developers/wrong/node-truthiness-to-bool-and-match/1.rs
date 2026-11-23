pub fn fee(amount: u32, is_member: bool) -> u32 {
    let rate = if is_member { 0 } else if amount >= 100 { 2 } else { 5 };
    if amount { amount + rate } else { 0 }
}
