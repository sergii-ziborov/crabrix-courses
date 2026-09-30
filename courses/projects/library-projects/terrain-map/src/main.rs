const HEX: &[u8] = b"0123456789abcdef";

fn noise(x: u32, y: u32) -> u32 {
    let mut value = x.wrapping_mul(374_761_393)
        ^ y.wrapping_mul(668_265_263);
    value = (value ^ (value >> 13))
        .wrapping_mul(1_274_126_177);
    value ^ (value >> 16)
}

fn main() {
    let (width, height) = (24, 16);
    let mut pixels = String::new();
    for y in 0..height {
        for x in 0..width {
            let edge = x.min(width - 1 - x)
                .min(y.min(height - 1 - y));
            let value = noise(x, y) % 100 + edge * 8;
            let color = match value {
                0..=38 => 0,
                39..=56 => 1,
                57..=82 => 2,
                83..=112 => 3,
                _ => 4,
            };
            pixels.push(HEX[color] as char);
        }
    }
    println!(
        r##"CRABRIX_CANVAS:{{"title":"Terrain Map","width":24,"height":16,"palette":["#082F49","#0EA5E9","#FDE68A","#22C55E","#F8FAFC"],"pixels":"{}"}}"##,
        pixels
    );
    println!("The same seed always rebuilds this island.");
}