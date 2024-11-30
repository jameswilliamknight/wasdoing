# Contexts

## Overview

Contexts help organize your documentation by project, task, or any other grouping you need. Each context maintains its own history and can output to separate files.

## Managing Contexts

```bash
# Create a new context
doc -n feature-x          # Create "feature-x" context
doc -n bug-fix           # Create "bug-fix" context
doc -n sprint-123        # Create "sprint-123" context

# Switch between contexts
doc -c feature-x         # Switch to feature-x context

# List available contexts
doc -l
📁 Available Contexts:
  ▶️  feature-x (active)
     bug-fix
     sprint-123
```

## Adding Entries

Each entry is automatically added to the active context:

```bash
# Switch to a context
doc -c feature-x

# Add entries to feature-x
doc -H "Started implementing new API"
doc -s "API design complete"

# Switch context and add entries
doc -c bug-fix
doc -H "Investigating memory leak"
doc -s "Fixed memory leak in worker thread"
```

## Context Storage

Each context gets its own SQLite database:

```
~/.was-doing/                # Or your custom location
└── tasks/             # Task databases
    ├── feature-x.db   # Feature work
    ├── bug-fix.db     # Bug fixes
    └── sprint-123.db  # Sprint tasks
```

### Database Schema

Each context database contains:

```sql
-- Entries table
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,           -- 'history' or 'summary'
    content TEXT NOT NULL,        -- Entry content
    timestamp DATETIME NOT NULL,  -- Creation time
    tags TEXT,                   -- Optional tags (comma-separated)
    metadata TEXT                -- JSON metadata
);

-- Index for faster timestamp queries
CREATE INDEX idx_timestamp ON entries(timestamp);
```

## Output Management

### Context-Specific Output Paths

Each context can have its own output configuration:

```bash
# Default output (uses context name)
doc -c feature-x              # Creates feature-x.md

# Custom output location
doc -c bug-fix -o bugs.md    # Creates bugs.md

# Multiple outputs
doc -c sprint-123 \
    -o sprint/current.md \   # Main documentation
    --daily daily.md \       # Daily summary
    --summary summary.md     # Sprint summary
```

## Best Practices

1. **Naming Contexts**
   - Use descriptive names
   - Stick to alphanumeric and underscores
   - Keep names concise but meaningful

2. **Context Organization**
   - One context per major feature/task
   - Separate contexts for different projects
   - Use sprint contexts for time-based organization

3. **Context Lifecycle**
   - Create contexts for long-running tasks
   - Use temporary contexts for short experiments
   - Archive completed contexts by exporting to PDF

4. **Output Organization**
   - Use consistent naming patterns
   - Create output directories per project
   - Include context name in filenames
   - Consider version control integration
