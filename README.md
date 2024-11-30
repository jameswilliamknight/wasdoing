# Was Doing (Work Documentation System)

A development-friendly work documentation system that helps you track what you're doing as you're doing it! 🚀

_This project started almost completely generated by Cursor AI! using `claude-3.5-sonnet-20241022`, so take everything with a grain of salt while the code is validated by humans._
🐦 _This canary clause will be removed when the code is fully validated._

## 🎯 New Here? Start Here!

**[Click here for our Friendly Onboarding Guide](docs/onboarding.md)** - We'll walk you through everything step by step!

## Quick Start

```bash
# Install
mkdir -p ~/.local/bin
ln -s "$(pwd)/doc" ~/.local/bin/doc

# First time setup
doc --setup

# Start documenting
doc -n my-project        # Create a context
doc -H "Started work"    # Add history
doc -w                   # Watch mode
```

## Command Reference

### Setup & Configuration
```bash
doc --setup              # Run interactive setup
doc --verify            # Check configuration
```

### Context Management
```bash
doc -c, --context NAME   # Switch to a context
doc -n, --new-context   # Create new context
doc -l, --list-contexts # List all contexts
```

### Entry Management
```bash
doc -H, --add-history   # Add history entry
doc -s, --add-summary   # Add summary entry
doc --history          # View history entries
doc --summary          # View summary entries
```

### Output Management
```bash
doc -w, --watch        # Watch mode: auto-regenerate
doc -r, --hot-reload   # Alias for --watch
doc -o, --output PATH  # Set output path
doc -e, --export PATH  # Export to PDF
```

## Documentation

Our documentation is organized into several sections:

-   [Installation Guide](docs/installation.md)

    -   System requirements
    -   Installation steps
    -   First time setup
    -   Troubleshooting

-   [Working with Contexts](docs/contexts.md)

    -   Creating and switching contexts
    -   Adding entries
    -   Best practices
    -   Storage structure

-   [Watch Mode Guide](docs/watch-mode.md)
    -   Real-time updates
    -   Context integration
    -   Terminal setup
    -   Common issues

-   [Database Implementation](docs/database.md)
    -   SQLite structure
    -   Data safety
    -   Backup procedures
    -   Performance tips

See our [complete documentation index](docs/index.md) for more guides and technical details.

## Project Structure 📁

```
was-doing/
├── 📄 __main__.py           # Entry Point & CLI
├── 📊 repository.py         # Data Layer
├── 📝 markdown_handler.py   # Document Generation
├── 👀 watcher.py           # File System Monitor
├── ⚙️ setup/               # Configuration
└── 📚 docs/                # Documentation
    └── wiki/              # Detailed guides
```

## Contributing 🤝

We love contributions! Here's how you can help:

1. **Fork & Clone**: Get your own copy to work on
2. **Branch**: Create a feature branch
3. **Code**: Make your changes
4. **Test**: Ensure everything works
5. **Push & PR**: Submit your contribution

All contributions are welcome:

-   🐛 Bug fixes
-   ✨ New features
-   📚 Documentation
-   🎨 UI improvements
-   🧪 Tests

Check out our [Contributing Guide](docs/contributing.md) for details.

## License 📜

This project is licensed under MIT + Commons Clause:

-   ✅ Free for personal use
-   ✅ Free for non-commercial projects
-   ✅ Modifications and improvements welcome
-   🤝 Commercial use requires permission

See [LICENSE](LICENSE) for details.

For commercial use inquiries, please contact jknightdev@gmail.com or visit [jknightdev.com](https://jknightdev.com).

## Development

-   [Project Structure](docs/project-structure.md)
-   [Contributing Guide](docs/contributing.md)
-   [Development Setup](docs/development.md)
