mod ui;

fn main() {
    println!("╭──── CRABRIX ORBIT CONTROL ────╮");
    for (name, value) in [("fuel", 82), ("signal", 67), ("oxygen", 94)] {
        println!("│ {:<8} {} {:>3}% │", name, ui::bar(value), value);
    }
    println!("╰──────── all systems local ────╯");
}