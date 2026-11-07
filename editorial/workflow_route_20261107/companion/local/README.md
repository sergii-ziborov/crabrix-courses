# Task Ledger — the complete on-device route

Open this personal copy through **Open Task Ledger** on a route lesson's Apply page.
A new copy has its own project identity. Opening, editing or downloading it never
starts a service or queries a database. Keep one personal copy as you progress.
Each of the 24 lessons also has a separate compiler lab with private checks.
The web Playground does not provide this native SQL host or loopback listener;
its lesson reading examples remain independent std-only programs.

## 1. Git: review and retain a source history

Set your real author identity with `git config user.name "Your Name"` and
`git config user.email you@example.com`, then use:

```sh
git init
git status
git diff src/main.rs
git commit -m "Add Task Ledger" -- Cargo.toml src/main.rs migrations/001.sql README.md
git branch feature-cli
git switch feature-cli
git log
```

Commit only reviewed paths. Switching requires a clean tree. The native profile
uses selected-path commits; it does not invent an independent staging area.
For one-file recovery, inspect an exact full commit with `git show COMMIT:PATH`;
`git restore --source COMMIT -- PATH` opens the existing confirmation preview.

## 2. CLI: arguments, configuration, input and errors

Initialize the real project-local database once:

```sh
sqlite3 tasks.db .read migrations/001.sql
cargo run --database tasks.db -- add "learn Rust"
env TASK_LIMIT=7 cargo run --database tasks.db -- list
cargo run -- import < input.txt
```

`--database` before Cargo's `--` is a Crabrix terminal extension granting this
invocation access to the named database. Arguments after `--` go unchanged to
Rust, including quoted spaces and empty strings. `env KEY=value` affects only
this invocation. A missing input file, invalid title or invalid limit must fail.
Create input.txt in the editor or with `echo 'one title' > input.txt`.
Import emits normalized JSON strings; it does not silently write those rows.

## 3. HTTP: execute the actual Rust handler

```sh
cargo serve --port 8080 --database tasks.db
curl -i http://127.0.0.1:8080/health
curl -i -H 'Content-Type: application/json' -H 'Idempotency-Key: request-1' -H 'X-Request-ID: req_42' -d '{"title":"learn SQL"}' http://127.0.0.1:8080/tasks
curl -i http://127.0.0.1:8080/tasks
http stop
```

The listener binds only to loopback. It supplies one real HTTP/1.x request on
stdin to a frozen, std-only Rust source snapshot, then sends the actual stdout
response over TCP. It supports Content-Length framing, not chunked requests or
HTTP pipelining. The host recalculates response byte length and closes the
connection. Stop/restart to use edited source. Leaving this project or entering
the background stops its listener. Preview pages retain their independent
network restrictions; this terminal command is an explicit network operation.

Repeat request-1 with the same title: expect 200 and the original task. Change
its title with the same key: expect 409. Missing keys and invalid titles return
400; unknown paths return 404; unsupported methods on known paths return 405.

## 4. SQL: durable constraints and observable failures

```sh
sqlite3 tasks.db 'SELECT id,title,done FROM tasks ORDER BY id'
sqlite3 tasks.db "INSERT INTO tasks(title,request_key) VALUES('', 'invalid')"
sqlite3 tasks.db 'EXPLAIN QUERY PLAN SELECT * FROM tasks WHERE request_key="request-1"'
```

The empty title is rejected by SQLite, independently of Rust. Database values
are bound through the host's JSON query interface; title text never becomes SQL
syntax. SQLite stores data under this personal project's identity, separately
from editable source and replaceable course downloads. It survives app relaunch;
source ZIPs and Git commits contain source, not this private database.

Use complete BEGIN..COMMIT or BEGIN..ROLLBACK scripts in one console invocation.
A failed open transaction is rolled back; an unfinished script is also rolled
back and reported. Already completed autocommit statements retain SQLite's usual
semantics. Queries have time, memory, row and output limits. The console supports
SQL and `.read`, rather than every command of the desktop sqlite3 executable.

## 5. Diagnostics: identify the failing boundary

Use the same request ID across related events. Inspect the terminal's actual
method/path/status receipt and X-Request-ID response. Distinguish request
validation, SQL constraint failure, Rust panic, listener startup and a stale
frozen snapshot. Never insert access tokens into saved example commands.
The desktop companion adds structured tracing, readiness and a real process log.

## 6. Delivery: verify the target that will actually run

```sh
cargo fmt --check
cargo test
cargo build
```

These commands check the native app's WASI profile. The `desktop/` companion is
a complete Axum + SQLx + SQLite server with its own Cargo.lock, acceptance probe,
Dockerfile, CI workflow and release script. Run its Linux/container and host
process steps on a desktop/server. iOS does not execute Docker, host shell
scripts or arbitrary Linux processes. A successful WASI run is not a desktop
server qualification.

Capstone acceptance: create through CLI, read through HTTP and SQL, reject an
invalid write, replay one request without duplication, restart the service and
retain its data. Then deliberately break a readiness condition in the desktop
profile and show that the previous known-good release remains available.

The editable request files have matching HTTP syntax highlighting. Send one with
`http run requests/health.http` or `http run requests/create.http`. Each file
contains one explicit request. Environment examples are configuration references;
neither this app nor the desktop sample loads .env files implicitly.
