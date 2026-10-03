fn next(seed: &mut u32) -> u32 {
    *seed = seed
        .wrapping_mul(1_664_525)
        .wrapping_add(1_013_904_223);
    *seed
}

fn main() {
    let mut seed = 0xC0FFEE;
    let mut counts = [0_u32; 6];
    for _ in 0..120 {
        let face = (next(&mut seed) % 6) as usize;
        counts[face] += 1;
    }
    for (index, count) in counts.iter().enumerate() {
        println!("{}  {:>3}", index + 1, count);
    }
}