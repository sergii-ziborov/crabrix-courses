#[derive(Debug, Clone, Copy, PartialEq)]
enum State {
    Todo,
    Doing,
    Done,
}

#[derive(Debug)]
struct Task {
    title: &'static str,
    state: State,
}

fn main() {
    let tasks = [
        Task { title: "learn match", state: State::Done },
        Task { title: "repair E0502", state: State::Doing },
        Task { title: "write tests", state: State::Todo },
    ];
    for task in &tasks {
        println!("{:?}  {}", task.state, task.title);
    }
    let done = tasks.iter()
        .filter(|task| task.state == State::Done)
        .count();
    println!("done {done}/{}", tasks.len());
}