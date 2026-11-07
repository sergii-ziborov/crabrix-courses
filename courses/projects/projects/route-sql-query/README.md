# Query the Right Rows in a Stable Order

Return a read-only query producing columns id,title,name for unfinished tasks in active projects. Tables are tasks(id,title,done,project_id) and projects(id,name,active); join on project_id=id, order by project name then task ID.

Terminal companion: Run sqlite3 tasks.db .read reports/pending.sql; compare the output after completing a task and archiving its project.

The private verification caller is supplied by the installed lesson. SQL-profile lessons require workflow-terminal-v1; they execute real SQLite in a fresh database. The complete Task Ledger source is in the route companion files.
