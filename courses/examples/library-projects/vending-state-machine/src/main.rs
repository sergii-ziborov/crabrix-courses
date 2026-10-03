#[derive(Debug, Clone, Copy)]
enum State {
    Waiting,
    Credit(u32),
}

#[derive(Debug, Clone, Copy)]
enum Event {
    Insert(u32),
    Buy { price: u32 },
    Cancel,
}

fn transition(state: State, event: Event) -> State {
    match (state, event) {
        (State::Waiting, Event::Insert(value)) => {
            State::Credit(value)
        }
        (State::Credit(total), Event::Insert(value)) => {
            State::Credit(total + value)
        }
        (State::Credit(total), Event::Buy { price })
            if total >= price => State::Credit(total - price),
        (_, Event::Cancel) => State::Waiting,
        (state, _) => state,
    }
}

fn main() {
    let events = [
        Event::Insert(50),
        Event::Insert(25),
        Event::Buy { price: 60 },
        Event::Cancel,
    ];
    let mut state = State::Waiting;
    for event in events {
        state = transition(state, event);
        println!("{state:?}");
    }
}