fn cycle_entry(next: &[usize]) -> usize {
    let (mut slow, mut fast) = (next[0], next[next[0]]);
    while slow != fast { slow = next[slow]; fast = next[next[fast]]; }
    slow = 0;
    while slow != fast { slow = next[slow]; fast = next[fast]; }
    slow
}

fn main() {
    let result = cycle_entry(&[1,2,3,1]).to_string();
    println!("{result}");
}
