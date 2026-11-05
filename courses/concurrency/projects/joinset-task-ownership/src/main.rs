use tokio::{runtime::Builder, task::JoinSet};
fn main() {
    let rt = Builder::new_current_thread()
        .build()
        .unwrap();
    rt.block_on(async {
        let mut tasks = JoinSet::new();
        for n in 0..4 {
            tasks.spawn(async move { (n, n * n) });
        }
        let mut results = Vec::new();
        while let Some(result) =
            tasks.join_next().await
        {
            results.push(result.unwrap());
        }
        results.sort_unstable();
        assert_eq!(
            results,
            [(0, 0), (1, 1), (2, 4), (3, 9)]
        );
    });
    println!("joinset-task-ownership: ok");
}

