# SQLite Database in Was Doing

Was Doing uses SQLite as its storage backend, providing a lightweight, serverless database solution that's perfect for personal task tracking. Each context (project) has its own SQLite database file, making it easy to manage and backup individual projects.

## Database Structure

### Location
- Each context's database is stored in `~/.wasdoing/tasks/{context_name}.db`
- Databases are automatically created when you create a new context

### Schema
The database uses a simple, single-table structure:

```sql
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,           -- 'history' or 'summary'
    content TEXT NOT NULL,        -- The actual entry content
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## Implementation Details

Was Doing uses a Repository pattern for database operations, providing a clean interface through the `WorkLogRepository` class. This ensures:

- Safe connection handling using context managers
- Proper error handling and reporting
- Type safety through dataclasses
- Clean separation of concerns

### Key Features

1. **Automatic Connection Management**
   ```python
   with repository._get_connection() as conn:
       # Database operations here
       # Connection automatically closed after use
   ```

2. **Entry Types**
   - `history`: Detailed work log entries
   - `summary`: High-level summary entries

3. **Error Handling**
   - `DatabaseError`: Base exception class
   - `ConnectionError`: For connection issues
   - `QueryError`: For query execution problems

## Common Operations

### Adding Entries
```bash
# Add a history entry
doc -H "Started working on feature X"

# Add a summary entry
doc -s "Completed authentication implementation"
```

### Viewing Entries
- Entries are automatically compiled into markdown
- Use watch mode to see real-time updates:
  ```bash
  doc -w
  ```

### Data Safety
- SQLite's ACID compliance ensures data integrity
- Each operation is wrapped in a transaction
- Automatic cleanup of connections prevents database locks

## Best Practices

1. **Regular Backups**
   - Backup the entire `~/.wasdoing/tasks/` directory
   - Each `.db` file is self-contained and portable

2. **Maintenance**
   - SQLite databases are self-maintaining
   - No vacuum or optimization needed for typical usage
   - Database files stay compact due to simple schema

3. **Performance**
   - SQLite handles thousands of entries efficiently
   - No need for indexing with typical usage patterns
   - Queries are optimized for timestamp-based retrieval