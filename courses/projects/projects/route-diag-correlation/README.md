# Propagate One Request Identity

Accept incoming IDs with 1..=64 bytes composed only of ASCII letters,digits,dash,underscore. Otherwise return the supplied fallback, which the caller guarantees is valid.

Terminal companion: Send curl -i -H "X-Request-ID: req_42" http://127.0.0.1:8080/health and follow the same ID through the diagnostic output.

The private verification caller is supplied by the installed lesson. SQL-profile lessons require workflow-terminal-v1; they execute real SQLite in a fresh database. The complete Task Ledger source is in the route companion files.
