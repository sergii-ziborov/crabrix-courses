fn is_prime(n: u64) -> bool {
    fn power(mut a: u64, mut d: u64, n: u64) -> u64 {
        let mut result = 1;
        while d > 0 {
            if d & 1 == 1 {
                result = (result as u128 * a as u128 % n as u128) as u64;
            }
            a = (a as u128 * a as u128 % n as u128) as u64;
            d >>= 1;
        }
        result
    }
    if n < 2 {
        return false;
    }
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] {
        if n % p == 0 {
            return n == p;
        }
    }
    let shifts = (n - 1).trailing_zeros();
    let d = (n - 1) >> shifts;
    // These seven bases cover unsigned 64-bit integers; u128 avoids overflow.
    for a in [2, 325, 9375, 28178, 450775, 9780504, 1795265022] {
        if a % n == 0 {
            continue;
        }
        let mut x = power(a % n, d, n);
        if x == 1 || x == n - 1 {
            continue;
        }
        let mut witness = true;
        for _ in 1..shifts {
            x = (x as u128 * x as u128 % n as u128) as u64;
            if x == n - 1 {
                witness = false;
                break;
            }
        }
        if witness {
            return false;
        }
    }
    true
}

fn main() {
    let result = is_prime(2147483647).to_string();
    println!("{result}");
}
