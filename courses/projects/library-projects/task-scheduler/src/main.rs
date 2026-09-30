#[derive(Debug)]
struct Job {
    name: &'static str,
    priority: u8,
    duration: u32,
}

fn main() {
    let mut jobs = vec![
        Job { name: "docs", priority: 2, duration: 3 },
        Job { name: "build", priority: 1, duration: 8 },
        Job { name: "tests", priority: 1, duration: 5 },
        Job { name: "archive", priority: 3, duration: 2 },
    ];
    jobs.sort_by_key(|job| (job.priority, job.duration));

    let mut clock = 0;
    for job in jobs {
        let start = clock;
        clock += job.duration;
        println!("{:>2}..{:>2}  {}", start, clock, job.name);
    }
}