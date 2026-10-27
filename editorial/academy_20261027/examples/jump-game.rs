fn can_reach(values: &[usize]) -> bool {
    if values.is_empty() {
        return false;
    }
    let mut farthest = 0;
    for (i, &jump) in values.iter().enumerate() {
        if i > farthest {
            return false;
        }
        farthest = farthest.max(i + jump);
        if farthest >= values.len() - 1 {
            return true;
        }
    }
    false
}

fn main() {
    let result = can_reach(&[2, 3, 1, 1, 4]).to_string();
    println!("{result}");
}
