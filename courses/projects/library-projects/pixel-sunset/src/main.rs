const HEX: &[u8] = b"0123456789abcdef";

fn main() {
    let width: usize = 24;
    let height: usize = 16;
    let mut pixels = String::new();

    for y in 0..height {
        for x in 0..width {
            let dx = x as i32 - 17;
            let dy = y as i32 - 6;
            let sun = dx * dx + dy * dy <= 9;
            let color = if sun {
                4
            } else if y < 5 {
                1
            } else if y < 9 {
                2
            } else if x.abs_diff(17) < 3 {
                4
            } else if (x + y) % 4 == 0 {
                5
            } else {
                3
            };
            pixels.push(HEX[color] as char);
        }
    }

    println!(
        r##"CRABRIX_CANVAS:{{"title":"Pixel Sunset","width":24,"height":16,"palette":["#111827","#312E81","#F97316","#0F766E","#FDE68A","#22D3EE"],"pixels":"{}"}}"##,
        pixels
    );
    println!("Edit the coordinates, then Run again.");
}