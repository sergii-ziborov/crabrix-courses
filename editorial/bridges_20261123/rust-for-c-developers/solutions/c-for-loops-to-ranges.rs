pub fn count_multiples(lo: u8, hi: u8, k: u8) -> u32 {
    let mut count = 0;
    for i in lo..=hi {
        if i % k == 0 {
            count += 1;
        }
    }
    count
}

pub fn first_power_at_least(n: u32) -> u32 {
    let mut p = 1;
    loop {
        if p >= n {
            break p;
        }
        p *= 2;
    }
}
