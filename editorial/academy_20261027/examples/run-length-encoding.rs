fn run_lengths(text: &str) -> String {
    let mut chars = text.chars();
    let Some(mut previous) = chars.next() else {
        return String::new();
    };
    let mut length = 1;
    let mut out = String::new();
    for current in chars {
        if current == previous {
            length += 1;
        } else {
            out.push(previous);
            out.push_str(&length.to_string());
            previous = current;
            length = 1;
        }
    }
    out.push(previous);
    out.push_str(&length.to_string());
    out
}

fn main() {
    let result = run_lengths("aaabbcaaaa").to_string();
    println!("{result}");
}
