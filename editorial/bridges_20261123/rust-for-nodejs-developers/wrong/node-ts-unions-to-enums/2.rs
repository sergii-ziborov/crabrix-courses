pub enum Shipment {
    Pending,
    Shipped { carrier: String, days: u32 },
    Delivered,
    Lost,
}

pub fn eta(s: &Shipment) -> String {
    match s {
        Shipment::Pending => String::from("not shipped yet"),
        Shipment::Shipped { carrier, days: 0 } => format!("arrives today via {carrier}"),
        Shipment::Shipped { carrier, days: 1 } => format!("1 day via {carrier}"),
        Shipment::Shipped { carrier, days } => format!("{days} days via {carrier}"),
        _ => String::from("delivered"),
    }
}
