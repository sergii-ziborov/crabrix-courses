fn deterministic_select(a:&[i32],k:usize)->i32 {
    assert!(k<a.len());
    if a.len()<=5 { let mut small=a.to_vec(); small.sort_unstable(); return small[k]; }
    let medians:Vec<_>=a.chunks(5).map(|group| { let mut g=group.to_vec(); g.sort_unstable(); g[g.len()/2] }).collect();
    let pivot=deterministic_select(&medians,medians.len()/2);
    let smaller:Vec<_>=a.iter().copied().filter(|&x|x<pivot).collect();
    let equal=a.iter().filter(|&&x|x==pivot).count();
    if k<smaller.len() { deterministic_select(&smaller,k) }
    else if k<smaller.len()+equal { pivot }
    else { let greater:Vec<_>=a.iter().copied().filter(|&x|x>pivot).collect(); deterministic_select(&greater,k-smaller.len()-equal) }
}

fn main() {
    let result = deterministic_select(&[12,3,5,7,4,19,26,1,9],4).to_string();
    println!("{result}");
}
