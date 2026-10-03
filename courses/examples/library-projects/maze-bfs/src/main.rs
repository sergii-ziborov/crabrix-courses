use std::collections::VecDeque;

const MAZE: [&str; 7] = [
    "############",
    "#S   #     #",
    "###  # ### #",
    "#    #   # #",
    "# #### # # #",
    "#      #  G#",
    "############",
];

fn main() {
    let start = (1_usize, 1_usize);
    let goal = (5_usize, 10_usize);
    let mut distance = [[usize::MAX; 12]; 7];
    let mut queue = VecDeque::from([start]);
    distance[start.0][start.1] = 0;

    while let Some((row, col)) = queue.pop_front() {
        for (dr, dc) in [(1_i32, 0_i32), (-1, 0), (0, 1), (0, -1)] {
            let next_row = (row as i32 + dr) as usize;
            let next_col = (col as i32 + dc) as usize;
            let open = MAZE[next_row].as_bytes()[next_col] != b'#';
            if open && distance[next_row][next_col] == usize::MAX {
                distance[next_row][next_col] = distance[row][col] + 1;
                queue.push_back((next_row, next_col));
            }
        }
    }
    println!("shortest path: {} steps", distance[goal.0][goal.1]);
}