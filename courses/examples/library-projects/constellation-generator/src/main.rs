// Change the seed, then Run again: both views will show a different sky.
const SEED: u32 = 0xC0FFEE;
const WIDTH: usize = 64;
const HEIGHT: usize = 40;
const STAR_COUNT: usize = 40;
const HEX: &[u8] = b"0123456789abcdef";
const PALETTE: [&str; 10] = [
    "#020617", "#071225", "#101E38", "#1B2E4F", "#294362", "#3D5B7A", "#6B9AC0", "#AACCE3",
    "#E7F4FF", "#F6D89A",
];

// A small deterministic sequence, not a source of secure randomness.
struct Rng32(u32);

impl Rng32 {
    fn next(&mut self) -> u32 {
        self.0 = self.0.wrapping_mul(1_664_525).wrapping_add(1_013_904_223);
        self.0
    }

    fn below(&mut self, limit: usize) -> usize {
        // Use the upper bits: the low bits of an LCG have short repeating cycles.
        ((self.next() >> 16) as usize) % limit
    }
}

fn terminal_sky(seed: u32) {
    let mut rng = Rng32(seed);
    println!("CRABRIX NIGHT SKY · seed {seed:#010X}");
    println!("┌{}┐", "─".repeat(38));
    for _ in 0..12 {
        let mut row = String::new();
        for _ in 0..38 {
            row.push(match rng.next() % 29 {
                0 => '✦',
                1..=3 => '·',
                _ => ' ',
            });
        }
        println!("│{row}│");
    }
    println!("└{}┘", "─".repeat(38));
}

fn paint(pixels: &mut [u8], x: i32, y: i32, color: u8) {
    // Every effect uses this clipped write, including halo pixels near an edge.
    if x >= 0 && y >= 0 && x < WIDTH as i32 && y < HEIGHT as i32 {
        let cell = &mut pixels[y as usize * WIDTH + x as usize];
        *cell = (*cell).max(color);
    }
}

fn draw_star(pixels: &mut [u8], x: i32, y: i32, bright: bool, warm: bool) {
    if bright {
        for dy in -2_i32..=2 {
            for dx in -2_i32..=2 {
                match dx.abs() + dy.abs() {
                    1 => paint(pixels, x + dx, y + dy, 6),
                    2 => paint(pixels, x + dx, y + dy, 4),
                    _ => {}
                }
            }
        }
    }
    paint(
        pixels,
        x,
        y,
        if warm {
            9
        } else if bright {
            8
        } else {
            7
        },
    );
}

fn canvas_sky(seed: u32) {
    let mut rng = Rng32(seed);
    let mut pixels = vec![0_u8; WIDTH * HEIGHT];

    // Faint diagonal haze with seeded dithering; integer math stays repeatable.
    for y in 0..HEIGHT {
        for x in 0..WIDTH {
            let jitter = rng.below(5) as i32 - 2;
            let distance = (2 * y as i32 - x as i32 / 2 - 20 + jitter).abs();
            let haze = match distance {
                0..=3 => 3,
                4..=7 => 2,
                8..=12 => 1,
                _ => 0,
            };
            let dust = rng.below(31) == 0;
            pixels[y * WIDTH + x] = if dust { 4 } else { haze };
        }
    }

    // Keep separate stars apart so their small halos remain legible.
    let mut stars: Vec<(i32, i32)> = Vec::new();
    for _ in 0..STAR_COUNT * 8 {
        if stars.len() == STAR_COUNT {
            break;
        }
        let x = 2 + rng.below(WIDTH - 4) as i32;
        let y = 2 + rng.below(HEIGHT - 4) as i32;
        if stars
            .iter()
            .any(|&(sx, sy)| (sx - x).abs() + (sy - y).abs() < 4)
        {
            continue;
        }
        let ordinal = stars.len() + 1;
        let bright = ordinal % 5 == 0;
        let warm = ordinal % 7 == 0;
        draw_star(&mut pixels, x, y, bright, warm);
        stars.push((x, y));
    }

    // One static meteor trail: a dim tail and a brighter head, no animation loop.
    for step in 1..=5 {
        paint(&mut pixels, 52 - step, 9 + step, (7 - step) as u8);
    }
    paint(&mut pixels, 52, 9, 8);

    let encoded: String = pixels.iter().map(|&p| HEX[p as usize] as char).collect();
    let palette = PALETTE
        .iter()
        .map(|color| format!("\"{color}\""))
        .collect::<Vec<_>>()
        .join(",");
    println!(
        "CRABRIX_CANVAS:{{\"title\":\"Constellation Generator\",\"width\":{WIDTH},\"height\":{HEIGHT},\"palette\":[{palette}],\"pixels\":\"{encoded}\"}}"
    );
    println!(
        "{} stars · subtle halos · faint nebula · one meteor trail",
        stars.len()
    );
    println!("Same seed, same sky. Edit SEED, STAR_COUNT or PALETTE and Run again.");
}

fn main() {
    terminal_sky(SEED);
    canvas_sky(SEED);
}
