fn solve_sudoku(grid:&mut [[u8;9];9])->bool {
    let empty=(0..9).flat_map(|r|(0..9).map(move |c|(r,c))).find(|&(r,c)|grid[r][c]==0);
    let Some((r,c))=empty else { return true; };
    for value in 1..=9 {
        let row=(0..9).all(|i|grid[r][i]!=value); let col=(0..9).all(|i|grid[i][c]!=value);
        let block=(r/3*3..r/3*3+3).all(|a|(c/3*3..c/3*3+3).all(|b|grid[a][b]!=value));
        if row && col && block { grid[r][c]=value; if solve_sudoku(grid) { return true; } grid[r][c]=0; }
    }
    false
}

fn main() {
    let result = { let mut grid=[[5,3,0,6,7,8,9,1,2],[6,7,2,1,9,5,3,4,8],[1,9,8,3,4,2,5,6,7],[8,5,9,7,6,1,4,2,3],[4,2,6,8,5,3,7,9,1],[7,1,3,9,2,4,8,5,6],[9,6,1,5,3,7,2,8,4],[2,8,7,4,1,9,6,3,5],[3,4,5,2,8,6,1,7,9]]; assert!(solve_sudoku(&mut grid)); grid[0][2].to_string() };
    println!("{result}");
}
