#[derive(Debug)]
enum Command {
    Add(String),
    Done(usize),
    List,
}

fn parse(input: &str) -> Result<Command, String> {
    let mut parts = input.trim().splitn(2, ' ');
    match (parts.next(), parts.next()) {
        (Some("add"), Some(title)) => {
            Ok(Command::Add(title.to_string()))
        }
        (Some("done"), Some(index)) => index
            .parse()
            .map(Command::Done)
            .map_err(|_| "bad index".to_string()),
        (Some("list"), None) => Ok(Command::List),
        _ => Err("unknown command".to_string()),
    }
}

fn main() {
    for input in ["add learn ownership", "done 2", "list", "erase"] {
        match parse(input) {
            Ok(Command::Add(title)) => println!("add: {title}"),
            Ok(Command::Done(index)) => println!("done: {index}"),
            Ok(Command::List) => println!("list"),
            Err(error) => println!("error: {error}"),
        }
    }
}