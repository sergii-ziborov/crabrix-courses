#[derive(Debug, Clone, Copy, PartialEq)]
enum Light {
    Red,
    Green,
    Yellow,
}

impl Light {
    fn next(self) -> Light {
        match self {
            Light::Red => Light::Green,
            Light::Green => Light::Yellow,
            Light::Yellow => Light::Red,
        }
    }

    fn seconds(self) -> u32 {
        match self {
            Light::Red => 30,
            Light::Green => 25,
            Light::Yellow => 5,
        }
    }
}

fn main() {
    let mut light = Light::Red;
    let mut clock = 0;

    for _ in 0..6 {
        println!("t={clock:>3}s  {:?} for {}s", light, light.seconds());
        clock += light.seconds();
        light = light.next();
    }
    println!("cycle returns to {:?}", light);
}