fn evaluate(input: &str) -> Result<f64, String> {
    let mut stack = Vec::new();
    for token in input.split_whitespace() {
        match token {
            "+" | "-" | "*" | "/" => {
                let right = stack.pop()
                    .ok_or("missing right operand")?;
                let left = stack.pop()
                    .ok_or("missing left operand")?;
                let value = match token {
                    "+" => left + right,
                    "-" => left - right,
                    "*" => left * right,
                    "/" => left / right,
                    _ => unreachable!(),
                };
                stack.push(value);
            }
            number => stack.push(
                number.parse::<f64>()
                    .map_err(|_| format!("bad token: {number}"))?
            ),
        }
    }
    stack.pop().ok_or("empty expression".to_string())
}

fn main() {
    for expression in ["3 4 +", "5 2 * 8 +", "9 3 / 2 -"] {
        println!("{expression:<12} {:?}", evaluate(expression));
    }
}