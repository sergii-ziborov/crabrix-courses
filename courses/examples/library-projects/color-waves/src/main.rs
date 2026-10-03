const HEX: &[u8] = b"0123456789abcdef";

fn main() {
    let (width, height) = (32, 16);
    let mut pixels = String::new();
    for y in 0..height {
        for x in 0..width {
            let wave = ((x as f64 * 0.45).sin()
                + (y as f64 * 0.70).cos()
                + ((x + y) as f64 * 0.18).sin())
                / 3.0;
            let color = ((wave + 1.0) * 2.5)
                .round() as usize;
            pixels.push(HEX[color.min(5)] as char);
        }
    }
    println!(
        r##"CRABRIX_CANVAS:{{"title":"Color Waves","width":32,"height":16,"palette":["#172554","#1D4ED8","#06B6D4","#34D399","#FACC15","#FB7185"],"pixels":"{}"}}"##,
        pixels
    );
    println!("Three waves sampled into 512 pixels.");
}