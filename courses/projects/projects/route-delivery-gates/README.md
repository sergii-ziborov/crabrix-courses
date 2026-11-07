# Make Checks Block Delivery

Require exactly one successful result for each of fmt,test,build. Missing, failed or duplicate required results refuse release; unrelated checks do not affect this contract.

Terminal companion: Run cargo fmt --check, cargo test and cargo build. Inspect the companion GitHub workflow for desktop integration checks.

The private verification caller is supplied by the installed lesson. SQL-profile lessons require workflow-terminal-v1; they execute real SQLite in a fresh database. The complete Task Ledger source is in the route companion files.
