// TypeScript original:
// type Shipment =
//   | { status: "pending" }
//   | { status: "shipped"; carrier: string; days: number }
//   | { status: "delivered" }
//   | { status: "lost" };
// function eta(s: Shipment): string {
//   switch (s.status) {
//     case "pending": return "not shipped yet";
//     case "shipped":
//       if (s.days === 0) return `arrives today via ${s.carrier}`;
//       return s.days === 1 ? `1 day via ${s.carrier}` : `${s.days} days via ${s.carrier}`;
//     case "delivered": return "delivered";
//     case "lost": return "lost";
//   }
// }
pub enum Shipment {
    Pending,
    Shipped { carrier: String, days: u32 },
    Delivered,
    Lost,
}

pub fn eta(s: &Shipment) -> String {
    todo!("implement the contract")
}
