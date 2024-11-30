# Project Structure

## Overview

The project follows a modular design with clear separation of concerns:

```
was-doing/
├── 📄 __main__.py           # Entry Point & CLI Handler
│   ├── 🎯 Command line argument parsing
│   ├── 🔄 Workflow orchestration
│   ├── 📝 Entry creation (history/summary)
│   ├── 🎮 User input/output handling
│   └── 📤 PDF export functionality
│
├── 📊 repository.py         # Data Layer
│   ├── 💾 SQLite database management
│   ├── 📝 Entry creation and retrieval
│   ├── 🔒 Data integrity checks
│   ├── 🔄 Database migrations
│   └── ⚠️ Error handling
│
├── 📝 markdown_handler.py   # Document Generation
│   ├── 📄 Markdown formatting
│   ├── 🎨 Template management
│   ├── 🔧 Content structuring
│   ├── 📦 Multiple output formats
│   └── 🎯 Consistent styling
│
├── 👀 watcher.py           # File System Monitor
│   ├── 🔄 Hot-reload functionality
│   ├── 🚦 Event handling
│   ├── 📡 Change detection
│   ├── 🔄 Auto-regeneration
│   └── ⚡ Watch mode lifecycle
│
├── ⚙️ setup/               # Configuration Management
│   ├── 📄 config.py
│   │   ├── 🔧 Config file management
│   │   ├── 🔍 Path resolution
│   │   ├── 🔒 Validation checks
│   │   ├── 📁 Directory management
│   │   └── 🔐 Permission handling
│   │
│   └── 📄 interactive.py   # Setup Wizard
│       ├── 🎯 User prompts
│       ├── 🔧 Initial setup
│       ├── 📋 System validation
│       ├── 📁 Directory creation
│       └── ✅ Requirement checks
│
├── 📄 requirements.txt     # Dependencies
│   ├── 📦 watchdog - File monitoring
│   ├── 📦 toml - Config parsing
│   ├── 📦 rich - Terminal UI
│   ├── 📦 inquirer - Interactive prompts
│   ├── 📦 markdown - MD processing
│   └── 📦 weasyprint - PDF generation
│
└── 📄 doc                 # Execution Script
```

## Data Storage Structure

```
~/.was-doing/                   # User Configuration
├── 📄 config.toml         # Main configuration
├── 📄 config_location     # Custom location pointer
├── 📁 tasks/             # Data Storage
│   ├── 📄 feature-x.db   # Context databases
│   └── 📄 bug-fix.db
├── 📁 templates/         # Custom templates
│   ├── 📄 default.md
│   └── 📄 daily.md
└── 📁 .venv/            # Virtual environment
```

## Database Schema

### Context Database (feature-x.db)

```sql
-- Entries table for storing history and summaries
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK (type IN ('history', 'summary')),
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tags TEXT,                    -- Comma-separated tags
    metadata TEXT                 -- JSON metadata
);

-- Indexes for performance
CREATE INDEX idx_entries_timestamp ON entries(timestamp);
CREATE INDEX idx_entries_type ON entries(type);
CREATE INDEX idx_entries_tags ON entries(tags);

-- Context metadata
CREATE TABLE context_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Template cache
CREATE TABLE template_cache (
    template_hash TEXT PRIMARY KEY,
    compiled_template TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration Format

### Main Configuration (config.toml)

```toml
# General Settings
[general]
default_context = "main"
watch_interval = 1.0
debug = false
max_history_entries = 1000

# Database Settings
[database]
path = "~/.was-doing/tasks"
backup_interval = "1d"
max_backup_size = "100M"
vacuum_threshold = "50M"

# Watch Mode Settings
[watch]
interval = 1.0
debounce = 0.5
max_cpu_percent = 50
max_memory_mb = 100
ignore_patterns = [".git/*", "*.tmp"]

# Output Settings
[output]
default_format = "markdown"
template_dir = "~/.was-doing/templates"
pdf_style = "github"
code_highlight = true

# Context Settings
[contexts]
auto_create = false
name_pattern = "^[a-zA-Z0-9_-]+$"
max_contexts = 50
```

## Template System

### Template Variables

```python
# Context Variables
${context.name}        # Current context name
${context.created}     # Context creation date
${context.path}        # Context database path
${context.meta.*}      # Context metadata

# Entry Variables
${entries.all}         # All entries
${entries.today}       # Today's entries
${entries.week}       # This week's entries
${entries.summaries}  # All summaries
${entries.history}    # All history entries
${entries.tagged.*}   # Entries with specific tag

# System Variables
${date}               # Current date
${time}               # Current time
${user}               # Current user
${version}            # Was Doing version
```

### Template Filters

```python
# Sorting and Limiting
${entries.today | sort}           # Sort entries
${entries.all | limit:10}         # Limit entries
${entries.tagged.bug | reverse}   # Reverse order

# Formatting
${content | wrap:80}             # Wrap text
${date | format:"%Y-%m-%d"}      # Format date
${tags | join:", "}              # Join lists

# Conditional
${entries | when:has_tag("bug")} # Conditional inclusion
${content | default:"No content"} # Default value
```

### Example Templates

```markdown
# Daily Report Template
# ${context.name} - ${date | format:"%A, %B %d"}

## Summary
${entries.today.summaries}

## Activities
${entries.today.history | sort}

## Tags
${entries.today | tags | unique | join:", "}

---
Generated by Was Doing v${version}
```

## Component Responsibilities

### Core Components

#### __main__.py - Entry Point
- Command-line interface
- Argument parsing
- Workflow orchestration
- Error handling
- User feedback

[... rest of the existing content ...]
