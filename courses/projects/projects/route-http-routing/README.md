# Route Method and Path Together

Match literal /tasks and /health after removing the query string. GET tasks=200, POST tasks=201, GET health=200; other methods on those paths=405, unknown paths=404.

Terminal companion: Run cargo serve --port 8080 --database tasks.db, then curl -i http://127.0.0.1:8080/tasks and curl -i -X DELETE http://127.0.0.1:8080/tasks. Stop with http stop.

The private verification caller is supplied by the installed lesson. SQL-profile lessons require workflow-terminal-v1; they execute real SQLite in a fresh database. The complete Task Ledger source is in the route companion files.
