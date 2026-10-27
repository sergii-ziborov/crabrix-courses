fn non_adjacent_sum(values:&[i32])->i32 {
    let (mut previous,mut best)=(0,0);
    for &value in values { let next=best.max(previous+value); previous=best; best=next; } best
}

fn main() {
    let result = non_adjacent_sum(&[2,7,9,3,1]).to_string();
    println!("{result}");
}
