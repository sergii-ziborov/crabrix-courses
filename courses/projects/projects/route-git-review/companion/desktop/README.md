# Task Ledger — desktop server profile

This profile runs real TCP, Axum, Tokio, SQLx and SQLite on the host. It is separate
from the app's stdin/loopback adapter. SQLx is configured without compile-time
query macros; values use bind parameters and idempotency is transactional.

```sh
cargo test --locked
cargo build --locked
python3 scripts/acceptance.py
cargo run --locked
```

Defaults: PORT=8080, DATABASE_URL=sqlite://tasks.db. Startup creates the initial
schema, validates required columns, then accepts traffic. `/health` is liveness;
`/ready` checks database availability. This initial teaching migration is not a
complete production migration manager. Subsequent schema revisions need an
explicit compatibility and migration policy.

POST /tasks accepts JSON `{ "title": "learn Rust" }` and an Idempotency-Key
header. Repeating the same key/title returns the original task; another title
returns 409. GET /tasks returns tasks in ID order. Each write uses a SQLx
transaction. The one-connection pool deliberately serializes this teaching
service; a larger pool requires separate contention and retry tests.

```sh
sh scripts/release.sh
docker build -t task-ledger:local .
docker run --rm -p 127.0.0.1:8080:8080 -v task-ledger-data:/data task-ledger:local
```

Commit reviewed changes first. The release script requires a clean checkout,
runs formatting, tests and build, records the source revision and toolchain,
computes the actual artifact SHA-256 and verifies it. It does not deploy or promote
a service. The Dockerfile runs as a non-root user with its database on a volume.
Check readiness before manually promoting a candidate; retain the prior image
and persistent-data compatibility before rolling back. The included CI workflow
runs the actual HTTP/SQL acceptance test on a clean build.

While the service runs, `python3 scripts/latency.py` records bounded concurrent GET
samples, successful-request nearest-rank p95 and the error count. Report the
failures alongside the percentile. `python3 scripts/retry_probe.py` demonstrates
a bounded client retry of readiness GET with a stable request ID; it exits 2
when the attempt/deadline budget is exhausted. It never retries writes. Stop the
service and compare its attempts with a successful run.
