fn main() {
    let log = "\
GET /index 200 12
POST /login 401 48
GET /assets 200 3
GET /index 200 27
POST /login 200 51
GET /missing 404 8";

    let entries: Vec<(&str, u32, u32)> = log
        .lines()
        .filter_map(|line| {
            let mut parts = line.split_whitespace();
            let _method = parts.next()?;
            let path = parts.next()?;
            let status: u32 = parts.next()?.parse().ok()?;
            let millis: u32 = parts.next()?.parse().ok()?;
            Some((path, status, millis))
        })
        .collect();

    let ok = entries.iter().filter(|(_, status, _)| *status == 200).count();
    let slowest = entries.iter().max_by_key(|(_, _, millis)| *millis);
    let total: u32 = entries.iter().map(|(_, _, millis)| millis).sum();

    println!("requests   {}", entries.len());
    println!("succeeded  {ok}");
    println!("total time {total}ms");
    if let Some((path, status, millis)) = slowest {
        println!("slowest    {path} ({status}) {millis}ms");
    }
}