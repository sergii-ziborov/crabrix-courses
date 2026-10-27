fn csv<T:std::fmt::Display>(a:impl IntoIterator<Item=T>)->String { a.into_iter().map(|x|x.to_string()).collect::<Vec<_>>().join(",") }
fn sparse_minima(values:&[i32],queries:&[(usize,usize)])->Vec<i32> {
    assert!(!values.is_empty()); let n=values.len(); let mut levels=vec![values.to_vec()]; let mut width=2;
    while width<=n {
        let previous=levels.last().unwrap(); let half=width/2;
        levels.push((0..=n-width).map(|i|previous[i].min(previous[i+half])).collect()); width*=2;
    }
    queries.iter().map(|&(left,right)| {
        let length=right-left+1; let level=length.ilog2() as usize; let width=1<<level;
        levels[level][left].min(levels[level][right+1-width])
    }).collect()
}

fn main() {
    let result = csv(sparse_minima(&[7,2,3,0,5,10,3,12,18],&[(0,3),(2,5),(4,6)]));
    println!("{result}");
}
