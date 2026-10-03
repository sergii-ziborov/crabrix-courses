fn bar(value: usize) -> String {
    "█".repeat(value)
}

fn main() {
    let samples = [
        ("Mon", 4),
        ("Tue", 9),
        ("Wed", 6),
        ("Thu", 12),
        ("Fri", 8),
    ];
    println!("LOCAL BUILDS");
    for (day, count) in samples {
        println!("{day} {:<12} {count}", bar(count));
    }
}