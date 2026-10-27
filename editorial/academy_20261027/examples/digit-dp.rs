fn digit_sum_count(bound: u64, target: usize) -> u64 {
    fn count(
        pos: usize,
        left: usize,
        tight: bool,
        digits: &[u8],
        memo: &mut [Vec<Option<u64>>],
    ) -> u64 {
        if pos == digits.len() {
            return u64::from(left == 0);
        }
        if !tight {
            if let Some(answer) = memo[pos][left] {
                return answer;
            }
        }
        let limit = if tight { digits[pos] } else { 9 };
        let mut answer = 0;
        for digit in 0..=limit {
            if digit as usize <= left {
                answer += count(
                    pos + 1,
                    left - digit as usize,
                    tight && digit == limit,
                    digits,
                    memo,
                );
            }
        }
        if !tight {
            memo[pos][left] = Some(answer);
        }
        answer
    }
    let digits: Vec<_> = bound.to_string().bytes().map(|c| c - b'0').collect();
    count(
        0,
        target,
        true,
        &digits,
        &mut vec![vec![None; target + 1]; digits.len()],
    )
}

fn main() {
    let result = digit_sum_count(25, 5).to_string();
    println!("{result}");
}
