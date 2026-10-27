fn contains_cycle(next: &[Option<usize>]) -> bool {
    // Arena indexes preserve node identity; None terminates a list.
    let (mut slow, mut fast) = (Some(0), Some(0));
    loop {
        slow = slow.and_then(|i| next[i]);
        fast = fast.and_then(|i| next[i]).and_then(|i| next[i]);
        if fast.is_none() {
            return false;
        }
        if slow == fast {
            return true;
        }
    }
}

fn main() {
    let result = contains_cycle(&[Some(1), Some(2), Some(3), Some(1)]).to_string();
    println!("{result}");
}
