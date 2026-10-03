fn celsius_to_fahrenheit(value: f64) -> f64 {
    value * 9.0 / 5.0 + 32.0
}

fn kilograms_to_pounds(value: f64) -> f64 {
    value * 2.204_622_621_8
}

fn main() {
    for value in [-20.0, 0.0, 21.5, 100.0] {
        println!(
            "{value:>6.1} C = {:>6.1} F",
            celsius_to_fahrenheit(value)
        );
    }
    println!("5 kg = {:.2} lb", kilograms_to_pounds(5.0));
}