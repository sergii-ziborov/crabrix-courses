// [dependencies.tokio]
// version = "1"
// default-features = false
// features = ["rt"]
// No runtime attribute macro is needed.
fn main() {
    use tokio::runtime::Builder;
    let runtime = Builder::new_current_thread()
        .build()
        .unwrap();
    let value = runtime.block_on(compute());
    println!("{value}");
}
async fn compute() -> u32 {
    42
}
