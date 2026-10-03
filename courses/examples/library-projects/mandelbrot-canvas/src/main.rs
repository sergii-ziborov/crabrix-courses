const HEX: &[u8] = b"0123456789abcdef";

fn main() {
    let width = 32;
    let height = 20;
    let mut pixels = String::new();

    for py in 0..height {
        for px in 0..width {
            let cx = px as f64 / width as f64 * 3.2 - 2.2;
            let cy = py as f64 / height as f64 * 2.2 - 1.1;
            let (mut x, mut y, mut step) = (0.0, 0.0, 0);
            while x * x + y * y <= 4.0 && step < 30 {
                let next_x = x * x - y * y + cx;
                y = 2.0 * x * y + cy;
                x = next_x;
                step += 1;
            }
            let color = if step == 30 { 0 } else {
                1 + step * 5 / 30
            };
            pixels.push(HEX[color] as char);
        }
    }
    println!(
        r##"CRABRIX_CANVAS:{{"title":"Mandelbrot Canvas","width":32,"height":20,"palette":["#020617","#1E1B4B","#4338CA","#7C3AED","#EC4899","#FDE047"],"pixels":"{}"}}"##,
        pixels
    );
    println!("640 points iterated with real Rust.");
}