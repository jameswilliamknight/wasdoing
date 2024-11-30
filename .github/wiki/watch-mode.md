# Watch Mode

Watch mode automatically monitors your work and generates documentation in real-time using filesystem events.

## Usage

```bash
# Start watch mode
doc -w

# Use custom output file
doc -w -o custom.md
```

## Configuration

The watch interval is a heartbeat timer that keeps the watcher running. The actual file changes are detected instantly using filesystem events:

```bash
# In config.toml
watch_interval = 1.0  # Default: 1 second heartbeat

# Or via command line
doc -w --interval 2.0
```

## Using with Contexts

```bash
# Watch specific context
doc -c feature-x -w

# Watch with custom output
doc -c bug-fix -w -o bugs.md
```

## Common Issues

If you encounter a "database locked" error:
- Wait a few seconds
- Check for other running instances
- Restart watch mode
