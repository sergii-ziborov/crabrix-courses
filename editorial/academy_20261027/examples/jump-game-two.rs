fn minimum_jumps(values:&[usize])->i32 {
    if values.is_empty() { return -1; } let (mut end,mut farthest,mut jumps)=(0,0,0);
    for i in 0..values.len()-1 {
        if i>farthest { return -1; } farthest=farthest.max(i+values[i]);
        if i==end { if farthest==end { return -1; } jumps+=1; end=farthest; if end>=values.len()-1 { break; } }
    } jumps
}

fn main() {
    let result = minimum_jumps(&[2,3,1,1,4]).to_string();
    println!("{result}");
}
