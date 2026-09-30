fn main() {
    let mut items = vec!["crab", "rust"];
    let first = &items[0];
    items.push("compiler");
    println!("{first}");
}