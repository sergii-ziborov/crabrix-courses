fn component_size(grid:&[Vec<i32>],start:(usize,usize))->usize {
    let (rows,cols)=(grid.len(),grid[0].len()); let target=grid[start.0][start.1];
    let mut seen=vec![vec![false;cols];rows]; let mut stack=vec![start]; let mut size=0;
    while let Some((r,c))=stack.pop() {
        if seen[r][c] || grid[r][c]!=target { continue; } seen[r][c]=true; size+=1;
        if r>0 { stack.push((r-1,c)); } if c>0 { stack.push((r,c-1)); }
        if r+1<rows { stack.push((r+1,c)); } if c+1<cols { stack.push((r,c+1)); }
    }
    size
}

fn main() {
    let result = component_size(&[vec![1,0,0],vec![1,1,0],vec![0,1,1]],(1,1)).to_string();
    println!("{result}");
}
