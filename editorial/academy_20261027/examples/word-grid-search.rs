fn word_exists(grid:&[Vec<u8>],word:&[u8])->bool {
    fn search(g:&[Vec<u8>],w:&[u8],r:usize,c:usize,i:usize,seen:&mut [Vec<bool>])->bool {
        if seen[r][c] || g[r][c]!=w[i] { return false; } if i+1==w.len() { return true; }
        seen[r][c]=true; let mut found=false;
        for (dr,dc) in [(-1,0),(1,0),(0,-1),(0,1)] {
            let (a,b)=(r as isize+dr,c as isize+dc);
            if a>=0 && b>=0 && a<g.len() as isize && b<g[0].len() as isize && search(g,w,a as usize,b as usize,i+1,seen) { found=true; break; }
        }
        seen[r][c]=false; found
    }
    if word.is_empty() { return true; } if grid.is_empty() { return false; }
    let mut seen=vec![vec![false;grid[0].len()];grid.len()];
    (0..grid.len()).any(|r|(0..grid[r].len()).any(|c|search(grid,word,r,c,0,&mut seen)))
}

fn main() {
    let result = word_exists(&["ABCE".as_bytes().to_vec(),"SFCS".as_bytes().to_vec(),"ADEE".as_bytes().to_vec()],"ABCCED".as_bytes()).to_string();
    println!("{result}");
}
