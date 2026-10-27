fn to_postfix(expression: &str) -> String {
    fn precedence(op: &str) -> u8 {
        match op {
            "+" | "-" => 1,
            "*" | "/" => 2,
            _ => 0,
        }
    }
    let (mut out, mut stack) = (Vec::new(), Vec::new());
    for token in expression.split_whitespace() {
        if token.parse::<i32>().is_ok() {
            out.push(token);
        } else if token == "(" {
            stack.push(token);
        } else if token == ")" {
            while stack.last() != Some(&"(") {
                out.push(stack.pop().expect("matching parenthesis"));
            }
            stack.pop();
        } else {
            while stack
                .last()
                .is_some_and(|&op| op != "(" && precedence(op) >= precedence(token))
            {
                out.push(stack.pop().unwrap());
            }
            stack.push(token);
        }
    }
    out.extend(stack.into_iter().rev());
    out.join(" ")
}

fn main() {
    let result = to_postfix("3 + 4 * 2").to_string();
    println!("{result}");
}
