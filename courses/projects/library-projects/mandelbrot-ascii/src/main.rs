const SHADES: [char; 8] = [' ', '.', ':', '-', '=', '+', '*', '#'];

fn escape(cx: f64, cy: f64, limit: u32) -> u32 {
    let (mut x, mut y) = (0.0_f64, 0.0_f64);
    let mut step = 0;
    while x * x + y * y <= 4.0 && step < limit {
        let next_x = x * x - y * y + cx;
        y = 2.0 * x * y + cy;
        x = next_x;
        step += 1;
    }
    step
}

fn main() {
    let limit = 60;
    for row in 0..24 {
        let mut line = String::new();
        for col in 0..64 {
            let cx = -2.2 + f64::from(col) * 3.0 / 64.0;
            let cy = -1.2 + f64::from(row) * 2.4 / 24.0;
            let steps = escape(cx, cy, limit);
            let index = (steps as usize * (SHADES.len() - 1)) / limit as usize;
            line.push(SHADES[index]);
        }
        println!("{line}");
    }
}