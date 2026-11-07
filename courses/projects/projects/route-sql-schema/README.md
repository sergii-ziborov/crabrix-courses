# Make Invalid Rows Impossible

Return DDL creating tasks(id INTEGER PRIMARY KEY,title TEXT NOT NULL,done INTEGER NOT NULL DEFAULT 0). Enforce a trimmed title length of 1..=80 and done IN (0,1) using SQL constraints.

Terminal companion: Run sqlite3 tasks.db .read migrations/001.sql, then attempt valid and invalid INSERT statements. The compiler lab executes your DDL against fresh real SQLite.

The private verification caller is supplied by the installed lesson. SQL-profile lessons require workflow-terminal-v1; they execute real SQLite in a fresh database. The complete Task Ledger source is in the route companion files.
