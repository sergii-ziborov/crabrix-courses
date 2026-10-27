fn climb_ways(n:usize)->u64 {
    let mut ways=vec![0;n+2]; ways[0]=1;
    for step in 1..=n { ways[step]=ways[step-1]+if step>=2 { ways[step-2] } else { 0 }; } ways[n]
}

fn main() {
    let result = climb_ways(5).to_string();
    println!("{result}");
}
