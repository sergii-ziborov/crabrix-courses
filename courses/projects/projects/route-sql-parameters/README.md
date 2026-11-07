# Bind Values Instead of SQL Syntax

Return a read-only query selecting task IDs with title exactly equal to parameter ?1, ordered by id. Table tasks has id and title columns; do not interpolate a title into SQL.

Terminal companion: Inspect the companion db::query call: the title travels in params, while SQL remains unchanged. Use a title containing an apostrophe in the HTTP request.

The private verification caller is supplied by the installed lesson. SQL-profile lessons require workflow-terminal-v1; they execute real SQLite in a fresh database. The complete Task Ledger source is in the route companion files.
