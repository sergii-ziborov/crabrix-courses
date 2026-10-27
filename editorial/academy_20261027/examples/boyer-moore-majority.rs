fn majority(values: &[i32]) -> i32 {
    // Contract: a strict majority exists. Without it, verify the candidate.
    let (mut candidate, mut balance) = (0, 0);
    for &x in values {
        if balance == 0 { candidate = x; }
        balance += if x == candidate { 1 } else { -1 };
    }
    candidate
}

fn main() {
    let result = majority(&[2,1,2,3,2,2,4]).to_string();
    println!("{result}");
}
