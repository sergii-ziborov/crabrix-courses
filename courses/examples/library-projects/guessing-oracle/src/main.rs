use std::cmp::Ordering;

fn main() {
    let secret = 73_u32;
    let (mut low, mut high) = (1_u32, 100_u32);
    let mut attempts = 0;

    loop {
        let guess = low + (high - low) / 2;
        attempts += 1;

        match guess.cmp(&secret) {
            Ordering::Equal => {
                println!("guess {attempts:>2}: {guess} — correct");
                break;
            }
            Ordering::Less => {
                println!("guess {attempts:>2}: {guess} — too low");
                low = guess + 1;
            }
            Ordering::Greater => {
                println!("guess {attempts:>2}: {guess} — too high");
                high = guess - 1;
            }
        }
    }

    println!("found in {attempts} guesses out of 100 possibilities");
}