#[derive(Debug)]
struct Expense {
    label: &'static str,
    amount: f64,
}

fn main() {
    let expenses = [
        Expense { label: "rent", amount: 850.0 },
        Expense { label: "food", amount: 126.4 },
        Expense { label: "books", amount: 42.5 },
    ];
    let total: f64 = expenses.iter()
        .map(|expense| expense.amount)
        .sum();

    println!("MONTHLY BUDGET");
    for expense in &expenses {
        println!("{:<10} {:>8.2}", expense.label, expense.amount);
    }
    println!("{:<10} {:>8.2}", "total", total);
}