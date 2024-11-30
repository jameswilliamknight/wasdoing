# Installation Guide

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Write permissions for chosen config directory

## Quick Start

```bash
# Create the bin directory if it doesn't exist
mkdir -p ~/.local/bin

# Create a symbolic link to the doc command
ln -s "$(pwd)/doc" ~/.local/bin/doc

# Verify installation
which doc
```

## First Time Setup

```bash
# Run the setup wizard
doc --setup
```

During setup, you'll be prompted to choose where to store your configuration and tasks:

1. **Default Location** (`~/.was-doing/`)

   - Standard Unix configuration location
   - Automatically backed up with home directory
   - Easy to find and manage

2. **Custom Location** (e.g., `~/Documents/work-docs/`)
   - Keep docs close to projects
   - Store on different drive
   - Share between machines (e.g., via Dropbox)

## Dependencies

The program uses several Python packages that are automatically installed in its virtual environment:

```bash
watchdog==3.0.0      # File system monitoring
toml==0.10.2        # Configuration parsing
rich==13.6.0        # Terminal UI enhancements
inquirer==3.1.3     # Interactive prompts
markdown==3.5.1     # Markdown processing
```

## Virtual Environment

The program maintains its own isolated Python environment:

```bash
~/.was-doing/
└── .venv/          # Virtual environment
    ├── bin/        # Python executables
    ├── lib/        # Python packages
    └── pyvenv.cfg  # Environment config
```

### Environment Management

The virtual environment is automatically:

1. Created on first run
2. Activated when running commands
3. Updated when dependencies change
4. Isolated from system Python

You don't need to manage it manually, but if needed:

```bash
# Manual environment reset
rm -rf ~/.was-doing/.venv
doc --setup

# Check environment
ls -la ~/.was-doing/.venv/bin
```

## Common Issues

1. **Command not found**

   ```bash
   # Ensure ~/.local/bin is in your PATH
   echo $PATH | grep ~/.local/bin
   ```

2. **Permission denied**

   ```bash
   # Check file permissions
   ls -l $(which doc)
   chmod +x doc
   ```

3. **Python environment issues**

   ```bash
   # Verify Python installation
   python3 --version
   pip3 --version
   ```

4. **Virtual Environment Issues**
   ```bash
   # Reset virtual environment
   rm -rf ~/.was-doing/.venv
   doc --setup
   ```
