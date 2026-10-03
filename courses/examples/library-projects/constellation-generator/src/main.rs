fn main() {
    let (width, height) = (38_u32, 12_u32);
    let mut seed = 0xC0FFEE_u32;
    println!("CRABRIX NIGHT SKY");
    for _ in 0..height {
        let mut row = String::new();
        for _ in 0..width {
            seed = seed.wrapping_mul(1_664_525).wrapping_add(1_013_904_223);
            row.push(match seed % 29 { 0 => '✦', 1..=3 => '·', _ => ' ' });
        }
        println!("│{row}│");
    }
}