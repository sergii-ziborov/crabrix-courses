fn main() {
    let log = "INFO compiler ready
WARN cache cold
ERROR parser failed
INFO cache warm
ERROR linker failed";
    let mut counts = [0_u32; 3];
    for line in log.lines() {
        let level = line.split_once(' ')
            .map(|pair| pair.0)
            .unwrap_or("UNKNOWN");
        match level {
            "INFO" => counts[0] += 1,
            "WARN" => counts[1] += 1,
            "ERROR" => counts[2] += 1,
            _ => {}
        }
    }
    println!("info  {}", counts[0]);
    println!("warn  {}", counts[1]);
    println!("error {}", counts[2]);
}