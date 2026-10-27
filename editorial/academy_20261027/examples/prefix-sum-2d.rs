fn rectangle_sum(a: &[Vec<i64>], r1: usize, c1: usize, r2: usize, c2: usize) -> i64 {
    let (rows, cols) = (a.len(), a[0].len());
    let mut p = vec![vec![0; cols+1]; rows+1];
    for r in 0..rows { for c in 0..cols {
        p[r+1][c+1] = a[r][c] + p[r][c+1] + p[r+1][c] - p[r][c];
    } }
    p[r2+1][c2+1] - p[r1][c2+1] - p[r2+1][c1] + p[r1][c1]
}

fn main() {
    let result = rectangle_sum(&[vec![1,2,3],vec![4,5,6],vec![7,8,9]],1,0,2,1).to_string();
    println!("{result}");
}
