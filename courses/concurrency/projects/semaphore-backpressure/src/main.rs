use std::sync::Arc;
use tokio::{
    runtime::Builder, sync::Semaphore,
    task::JoinSet,
};
fn main() {
    Builder::new_current_thread()
        .build()
        .unwrap()
        .block_on(async {
            let limit = Arc::new(Semaphore::new(2));
            let mut tasks = JoinSet::new();
            for n in 0..6 {
                let permit = limit
                    .clone()
                    .acquire_owned()
                    .await
                    .unwrap();
                tasks.spawn(async move {
                    let _permit = permit;
                    tokio::task::yield_now().await;
                    n * 2
                });
            }
            let mut results = Vec::new();
            while let Some(value) =
                tasks.join_next().await
            {
                results.push(value.unwrap());
            }
            results.sort_unstable();
            assert_eq!(
                results,
                [0, 2, 4, 6, 8, 10]
            );
            assert_eq!(
                limit.available_permits(),
                2
            );
        });
    println!("semaphore-backpressure: ok");
}

