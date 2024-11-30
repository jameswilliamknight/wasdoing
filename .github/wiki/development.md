# Development Setup

## Environment Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/jameswilliamknight/wasdoing.git
   cd wasdoing
   ```

2. **Python Environment**
   ```bash
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

   # Install development tools
   pip install black mypy pylint pytest
   ```

3. **Development Installation**
   ```bash
   # Create development symlink
   mkdir -p ~/.local/bin
   ln -s "$(pwd)/doc" ~/.local/bin/doc-dev

   # Verify installation
   which doc-dev
   ```

## Development Tools

1. **Code Formatting**
   ```bash
   # Format code
   black .

   # Check only
   black . --check
   ```

2. **Type Checking**
   ```bash
   # Check types
   mypy .

   # Generate stubs
   mypy --generate-stubs
   ```

3. **Linting**
   ```bash
   # Run pylint
   pylint wasdoing

   # Run specific checks
   pylint wasdoing --disable=C0111
   ```

4. **Testing**
   ```bash
   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_repository.py

   # Run with coverage
   pytest --cov=wasdoing
   ```

## Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Run Tests**
   ```bash
   # Before changes
   pytest

   # Make changes

   # After changes
   pytest
   black .
   mypy .
   pylint wasdoing
   ```

3. **Local Testing**
   ```bash
   # Test installation
   doc-dev --setup

   # Test features
   doc-dev -n test-context
   doc-dev -H "Testing new feature"
   ```

## Common Tasks

1. **Database Management**
   ```bash
   # Reset test database
   rm -f tests/data/*.db

   # Create test data
   python tests/create_test_data.py
   ```

2. **Documentation**
   ```bash
   # Generate API docs
   pdoc --html wasdoing

   # Serve documentation
   python -m http.server -d docs/html
   ```

3. **Debugging**
   ```bash
   # Enable debug logging
   export WAS_DOING_DEBUG=1
   doc-dev -H "Test entry"

   # Run with debugger
   python -m pdb __main__.py
   ```

## Project Layout

```
was-doing/
├── src/                 # Source code
├── tests/              # Test files
├── docs/               # Documentation
│   └── wiki/          # Wiki pages
├── scripts/            # Development scripts
└── .github/            # GitHub configuration
```

## Configuration

1. **Development Config**
   ```toml
   # ~/.was-doing/config-dev.toml
   debug = true
   watch_interval = 0.5
   test_mode = true
   ```

2. **Test Data**
   ```bash
   # Generate test entries
   python scripts/generate_test_data.py
   ```

## Troubleshooting

1. **Virtual Environment**
   ```bash
   # Reset venv
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Database Issues**
   ```bash
   # Check SQLite
   sqlite3 ~/.was-doing/tasks/default.db .tables
   ```

3. **Permission Problems**
   ```bash
   # Fix permissions
   chmod +x doc
   chmod 644 ~/.was-doing/config.toml
   ```
