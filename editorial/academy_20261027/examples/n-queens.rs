fn queens(n: usize) -> usize {
    fn place(row: usize, n: usize, cols: &mut [bool], down: &mut [bool], up: &mut [bool]) -> usize {
        if row == n {
            return 1;
        }
        let mut count = 0;
        for c in 0..n {
            let (d, u) = (row + c, row + n - 1 - c);
            if !cols[c] && !down[d] && !up[u] {
                cols[c] = true;
                down[d] = true;
                up[u] = true;
                count += place(row + 1, n, cols, down, up);
                cols[c] = false;
                down[d] = false;
                up[u] = false;
            }
        }
        count
    }
    if n == 0 {
        return 1;
    }
    place(
        0,
        n,
        &mut vec![false; n],
        &mut vec![false; 2 * n - 1],
        &mut vec![false; 2 * n - 1],
    )
}

fn main() {
    let result = queens(5).to_string();
    println!("{result}");
}
