fn to_fahrenheit(celsius: f64) -> f64 {
    celsius * 9.0 / 5.0 + 32.0
}

fn main() {
    println!("{:>8} {:>12} {:>10}", "CELSIUS", "FAHRENHEIT", "KELVIN");
    for step in 0..=10 {
        let celsius = -20.0 + f64::from(step) * 5.0;
        println!(
            "{:>8.1} {:>12.1} {:>10.2}",
            celsius,
            to_fahrenheit(celsius),
            celsius + 273.15
        );
    }
}