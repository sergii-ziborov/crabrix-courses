fn parentheses(n: usize) -> Vec<String> {
    fn visit(n: usize, open: usize, closed: usize, text: &mut String, out: &mut Vec<String>) {
        if closed == n {
            out.push(text.clone());
            return;
        }
        if open < n {
            text.push('(');
            visit(n, open + 1, closed, text, out);
            text.pop();
        }
        if closed < open {
            text.push(')');
            visit(n, open, closed + 1, text, out);
            text.pop();
        }
    }
    let mut out = Vec::new();
    visit(n, 0, 0, &mut String::new(), &mut out);
    out
}

fn main() {
    let result = parentheses(3).join(";");
    println!("{result}");
}
