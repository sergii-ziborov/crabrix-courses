#[derive(Debug, Clone, Copy)]
struct Sample {
    celsius: f64,
    humidity: u8,
}

fn main() {
    let samples = [
        Sample { celsius: 21.4, humidity: 58 },
        Sample { celsius: 22.1, humidity: 55 },
        Sample { celsius: 20.8, humidity: 61 },
        Sample { celsius: 23.0, humidity: 52 },
    ];
    let average = samples.iter()
        .map(|sample| sample.celsius)
        .sum::<f64>() / samples.len() as f64;
    let driest = samples.iter()
        .min_by_key(|sample| sample.humidity)
        .unwrap();
    println!("average {average:.1} C");
    println!("driest  {}%", driest.humidity);
}