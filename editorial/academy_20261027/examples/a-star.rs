fn grid_a_star(rows: usize, cols: usize, start: (usize, usize), goal: (usize, usize)) -> usize {
    let heuristic = |(r, c): (usize, usize)| r.abs_diff(goal.0) + c.abs_diff(goal.1);
    let mut distance = vec![vec![usize::MAX; cols]; rows];
    distance[start.0][start.1] = 0;
    let mut heap =
        std::collections::BinaryHeap::from([std::cmp::Reverse((heuristic(start), 0, start))]);
    while let Some(std::cmp::Reverse((_, cost, (r, c)))) = heap.pop() {
        if cost != distance[r][c] {
            continue;
        }
        if (r, c) == goal {
            return cost;
        }
        for (dr, dc) in [(-1, 0), (1, 0), (0, -1), (0, 1)] {
            let (nr, nc) = (r as isize + dr, c as isize + dc);
            if nr < 0 || nc < 0 || nr >= rows as isize || nc >= cols as isize {
                continue;
            }
            let next = (nr as usize, nc as usize);
            if cost + 1 < distance[next.0][next.1] {
                distance[next.0][next.1] = cost + 1;
                heap.push(std::cmp::Reverse((
                    cost + 1 + heuristic(next),
                    cost + 1,
                    next,
                )));
            }
        }
    }
    unreachable!("empty grid has a path")
}

fn main() {
    let result = grid_a_star(4, 4, (0, 0), (3, 2)).to_string();
    println!("{result}");
}
