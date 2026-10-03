const WIDTH: usize = 32;
const HEIGHT: usize = 16;

fn neighbours(grid: &[[bool; WIDTH]; HEIGHT], row: usize, col: usize) -> usize {
    let mut count = 0;
    for delta_row in [HEIGHT - 1, 0, 1] {
        for delta_col in [WIDTH - 1, 0, 1] {
            if delta_row == 0 && delta_col == 0 {
                continue;
            }
            let r = (row + delta_row) % HEIGHT;
            let c = (col + delta_col) % WIDTH;
            if grid[r][c] {
                count += 1;
            }
        }
    }
    count
}

fn step(grid: &[[bool; WIDTH]; HEIGHT]) -> [[bool; WIDTH]; HEIGHT] {
    let mut next = [[false; WIDTH]; HEIGHT];
    for row in 0..HEIGHT {
        for col in 0..WIDTH {
            next[row][col] = matches!(
                (grid[row][col], neighbours(grid, row, col)),
                (true, 2) | (true, 3) | (false, 3)
            );
        }
    }
    next
}

fn main() {
    let mut grid = [[false; WIDTH]; HEIGHT];
    // A glider.
    for (row, col) in [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)] {
        grid[row][col] = true;
    }

    for generation in 0..4 {
        println!("generation {generation}");
        for row in grid.iter() {
            let line: String = row.iter().map(|&on| if on { '#' } else { '.' }).collect();
            println!("{line}");
        }
        println!();
        grid = step(&grid);
    }
}