fn fibonacci(n: usize) -> u64 {
    fn compute(n: usize, memo: &mut [Option<u64>]) -> u64 {
        if let Some(answer) = memo[n] {
            return answer;
        }
        let answer = if n < 2 {
            n as u64
        } else {
            compute(n - 1, memo) + compute(n - 2, memo)
        };
        memo[n] = Some(answer);
        answer
    }
    assert!(n <= 93);
    compute(n, &mut vec![None; n + 1])
}

fn main() {
    let result = fibonacci(12).to_string();
    println!("{result}");
}
