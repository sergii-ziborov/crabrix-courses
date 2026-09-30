#[derive(Debug)]
struct Sale {
    region: String,
    product: String,
    units: u32,
    unit_price: f64,
}

impl Sale {
    fn total(&self) -> f64 {
        f64::from(self.units) * self.unit_price
    }
}

fn parse(line: &str) -> Option<Sale> {
    let mut fields = line.split(',');
    Some(Sale {
        region: fields.next()?.trim().to_string(),
        product: fields.next()?.trim().to_string(),
        units: fields.next()?.trim().parse().ok()?,
        unit_price: fields.next()?.trim().parse().ok()?,
    })
}

fn main() {
    let raw = "\
north, keyboard, 12, 49.99
south, monitor, 4, 219.50
north, mouse, 30, 19.95
east, monitor, 7, 219.50
south, keyboard, 9, 49.99";

    let sales: Vec<Sale> = raw.lines().filter_map(parse).collect();
    println!("{} rows parsed", sales.len());

    let mut regions: Vec<&str> = sales.iter().map(|s| s.region.as_str()).collect();
    regions.sort_unstable();
    regions.dedup();

    for region in regions {
        let total: f64 = sales
            .iter()
            .filter(|s| s.region == region)
            .map(Sale::total)
            .sum();
        println!("{region:<8} {total:>10.2}");
    }
}