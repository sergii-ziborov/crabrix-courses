#[derive(Debug, PartialEq)]
enum Token {
    Number(f64),
    Plus,
    Minus,
    Star,
    Slash,
    LeftParen,
    RightParen,
}

fn tokenize(input: &str) -> Result<Vec<Token>, String> {
    let mut tokens = Vec::new();
    let mut chars = input.chars().peekable();

    while let Some(&character) = chars.peek() {
        match character {
            ' ' => { chars.next(); }
            '+' => { chars.next(); tokens.push(Token::Plus); }
            '-' => { chars.next(); tokens.push(Token::Minus); }
            '*' => { chars.next(); tokens.push(Token::Star); }
            '/' => { chars.next(); tokens.push(Token::Slash); }
            '(' => { chars.next(); tokens.push(Token::LeftParen); }
            ')' => { chars.next(); tokens.push(Token::RightParen); }
            digit if digit.is_ascii_digit() || digit == '.' => {
                let mut number = String::new();
                while let Some(&next) = chars.peek() {
                    if next.is_ascii_digit() || next == '.' {
                        number.push(next);
                        chars.next();
                    } else {
                        break;
                    }
                }
                let value = number
                    .parse()
                    .map_err(|_| format!("bad number: {number}"))?;
                tokens.push(Token::Number(value));
            }
            other => return Err(format!("unexpected character: {other}")),
        }
    }
    Ok(tokens)
}

fn main() {
    for input in ["3 + 4 * (2 - 1)", "10 / 2.5", "1 + $"] {
        match tokenize(input) {
            Ok(tokens) => println!("{input:<18} -> {} tokens {:?}", tokens.len(), tokens),
            Err(error) => println!("{input:<18} -> error: {error}"),
        }
    }
}