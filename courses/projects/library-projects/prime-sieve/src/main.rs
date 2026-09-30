fn sieve(limit: usize) -> Vec<usize> {
    let mut is_prime = vec![true; limit + 1];
    is_prime[0] = false;
    if limit >= 1 {
        is_prime[1] = false;
    }

    let mut value = 2;
    while value * value <= limit {
        if is_prime[value] {
            let mut multiple = value * value;
            while multiple <= limit {
                is_prime[multiple] = false;
                multiple += value;
            }
        }
        value += 1;
    }

    is_prime
        .iter()
        .enumerate()
        .filter(|(_, prime)| **prime)
        .map(|(index, _)| index)
        .collect()
}

fn main() {
    let primes = sieve(200);
    println!("{} primes below 200", primes.len());
    for chunk in primes.chunks(10) {
        let row: Vec<String> = chunk.iter().map(|p| format!("{p:>4}")).collect();
        println!("{}", row.join(" "));
    }
}