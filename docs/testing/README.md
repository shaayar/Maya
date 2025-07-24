# MAYA AI Chatbot - Testing Documentation

This directory contains comprehensive testing documentation for the MAYA AI Chatbot project. The documentation is organized by module and test type to help developers understand and verify the functionality of different components.

## Directory Structure

```
docs/testing/
├── README.md                 # This file
├── test_data/                # Test data and fixtures
├── modules/                  # Module-specific test guides
│   ├── voice_tests.md        # Voice feature testing
│   ├── character_tests.md    # Anime character mode testing
│   ├── video_tests.md        # Video playback testing
│   ├── todo_tests.md         # To-Do list feature testing
│   └── file_tests.md         # File operations testing
├── unit_tests.md             # Unit testing guidelines
├── integration_tests.md      # Integration testing procedures
└── ui_tests.md               # User interface testing
```

## Getting Started

### Prerequisites
- Python 3.8+
- Required packages (install with `pip install -r requirements-dev.txt`)
- Test data (if any) in the `test_data/` directory

### Running Tests

1. **Unit Tests**
   ```bash
   python -m pytest tests/unit
   ```

2. **Integration Tests**
   ```bash
   python -m pytest tests/integration
   ```

3. **UI Tests**
   ```bash
   python -m pytest tests/ui
   ```

## Test Coverage

To generate a test coverage report:

```bash
coverage run -m pytest
coverage report -m
```

## Writing New Tests

When adding new features, please include corresponding tests. Follow these guidelines:

1. Create test files in the appropriate test directory
2. Follow the naming convention `test_*.py`
3. Include docstrings explaining test cases
4. Use fixtures for common test data

## Reporting Issues

If you encounter any issues with the tests:
1. Check the test output for errors
2. Verify your environment setup
3. If the issue persists, please file a bug report with:
   - Test that's failing
   - Expected vs actual behavior
   - Steps to reproduce
   - Environment details

## Contributing

Contributions to improve test coverage and quality are welcome! Please follow the contribution guidelines in the main project README.
