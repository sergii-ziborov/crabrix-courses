type Matrix = Vec<Vec<i32>>;

fn multiply(left: &Matrix, right: &Matrix) -> Matrix {
    let rows = left.len();
    let inner = right.len();
    let cols = right[0].len();
    let mut out = vec![vec![0_i32; cols]; rows];

    for row in 0..rows {
        for col in 0..cols {
            let mut sum: i32 = 0;
            for k in 0..inner {
                sum += left[row][k] * right[k][col];
            }
            out[row][col] = sum;
        }
    }
    out
}

fn show(label: &str, matrix: &Matrix) {
    println!("{label}");
    for row in matrix {
        let cells: Vec<String> = row.iter().map(|v| format!("{v:>6}")).collect();
        println!("  [{}]", cells.join(" "));
    }
}

fn main() {
    let a: Matrix = vec![vec![1, 2, 3], vec![4, 5, 6]];
    let b: Matrix = vec![vec![7, 8], vec![9, 10], vec![11, 12]];
    show("A", &a);
    show("B", &b);
    show("A x B", &multiply(&a, &b));
}