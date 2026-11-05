use tokio::{
    runtime::Builder, sync::watch, task::JoinSet,
};
fn main() {
    Builder::new_current_thread()
        .build()
        .unwrap()
        .block_on(async {
            let (stop, receiver) =
                watch::channel(false);
            let mut tasks = JoinSet::new();
            for _ in 0..2 {
                let mut rx = receiver.clone();
                tasks.spawn(async move {
                    loop {
                        if *rx.borrow() {
                            break;
                        }
                        if rx
                            .changed()
                            .await
                            .is_err()
                        {
                            break;
                        }
                    }
                    "stopped"
                });
            }
            stop.send(true).unwrap();
            let mut stopped = 0;
            while let Some(result) =
                tasks.join_next().await
            {
                assert_eq!(
                    result.unwrap(),
                    "stopped"
                );
                stopped += 1;
            }
            assert_eq!(stopped, 2);
        });
    println!("graceful-shutdown-protocol: ok");
}

