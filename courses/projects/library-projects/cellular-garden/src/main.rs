const W: usize = 24;
const H: usize = 16;

fn neighbors(grid: &[bool], x: usize, y: usize) -> u8 {
    let mut total = 0;
    for dy in [-1_i32, 0, 1] {
        for dx in [-1_i32, 0, 1] {
            if dx == 0 && dy == 0 { continue; }
            let nx = x as i32 + dx;
            let ny = y as i32 + dy;
            if nx >= 0 && ny >= 0
                && nx < W as i32 && ny < H as i32
                && grid[ny as usize * W + nx as usize]
            {
                total += 1;
            }
        }
    }
    total
}

fn main() {
    let mut grid = vec![false; W * H];
    for (x, y) in [
        (4, 5), (5, 6), (3, 7), (4, 7), (5, 7),
        (14, 4), (15, 4), (16, 4), (16, 5),
    ] {
        grid[y * W + x] = true;
    }

    let mut next = vec![false; W * H];
    for y in 0..H {
        for x in 0..W {
            let count = neighbors(&grid, x, y);
            next[y * W + x] = count == 3
                || (grid[y * W + x] && count == 2);
        }
    }
    let pixels: String = next.iter()
        .map(|alive| if *alive { '2' } else { '0' })
        .collect();
    println!(
        r##"CRABRIX_CANVAS:{{"title":"Cellular Garden","width":24,"height":16,"palette":["#071A13","#166534","#4ADE80"],"pixels":"{}"}}"##,
        pixels
    );
    println!("One generation evolved locally.");
}