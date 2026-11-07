# Commit Related Changes Atomically

Return a complete BEGIN..COMMIT SQLite script transferring amount from account 1 to 2. accounts(id,balance) enforces balance>=0. Debit and credit must be atomic, including overdraw failure. Amount is a trusted u32 numeric value.

Terminal companion: Run sqlite3 ledger.db .read migrations/accounts.sql. Execute a valid BEGIN..COMMIT transfer and an overdraw script, then SELECT both balances.

The private verification caller is supplied by the installed lesson. SQL-profile lessons require workflow-terminal-v1; they execute real SQLite in a fresh database. The complete Task Ledger source is in the route companion files.
