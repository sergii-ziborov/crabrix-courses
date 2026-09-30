#[derive(Debug)]
enum Event {
    BuildPassed,
    Diagnostic(String),
}

trait Handler {
    fn handle(&mut self, event: &Event);
}

struct Counter(usize);

impl Handler for Counter {
    fn handle(&mut self, _event: &Event) {
        self.0 += 1;
        println!("events seen: {}", self.0);
    }
}

struct Reporter;

impl Handler for Reporter {
    fn handle(&mut self, event: &Event) {
        match event {
            Event::BuildPassed => println!("build passed"),
            Event::Diagnostic(text) => println!("diagnostic: {text}"),
        }
    }
}

fn main() {
    let mut handlers: Vec<Box<dyn Handler>> = vec![
        Box::new(Counter(0)),
        Box::new(Reporter),
    ];
    let events = [
        Event::BuildPassed,
        Event::Diagnostic("E0502".to_string()),
    ];
    for event in &events {
        for handler in &mut handlers {
            handler.handle(event);
        }
    }
}