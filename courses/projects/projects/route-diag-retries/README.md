# Bound the Retry Budget

Return true only for a transient failure with 1<=failed_attempts<maximum and checked delay+operation_budget<=remaining. Overflow refuses the retry.

Terminal companion: Run python3 scripts/retry_probe.py against the desktop readiness endpoint. Stop the service and repeat; inspect the bounded attempt count and request ID. This probe retries an idempotent client GET, rather than automatically retrying service writes.

The private verification caller is supplied by the installed lesson. SQL-profile lessons require workflow-terminal-v1; they execute real SQLite in a fresh database. The complete Task Ledger source is in the route companion files.
