fn postfix(expression:&str)->i32 {
    let mut stack=Vec::new();
    for token in expression.split_whitespace() {
        if let Ok(value)=token.parse::<i32>() { stack.push(value); continue; }
        let right=stack.pop().unwrap(); let left=stack.pop().unwrap();
        stack.push(match token { "+"=>left+right, "-"=>left-right, "*"=>left*right, "/"=>left/right, _=>panic!("operator") });
    }
    assert_eq!(stack.len(),1); stack[0]
}

fn main() {
    let result = postfix("2 7 + 3 * 4 -").to_string();
    println!("{result}");
}
