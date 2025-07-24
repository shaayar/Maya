# Unit Testing Guidelines

This document provides guidelines for writing and running unit tests for the MAYA AI Chatbot project.

## Test Structure

### Directory Layout
```
tests/
├── unit/
│   ├── __init__.py
│   ├── test_voice.py
│   ├── test_character.py
│   ├── test_video.py
│   └── ...
└── conftest.py
```

### Naming Conventions
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

## Writing Tests

### Example Test
```python
def test_character_trait_creation():
    """Test creating a character trait with valid parameters."""
    trait = CharacterTrait(
        name="Test",
        description="Test trait",
        pitch_modifier=0.5,
        speed_modifier=1.0
    )
    assert trait.name == "Test"
    assert 0.4 < trait.pitch_modifier < 0.6
```

### Best Practices
1. **Isolation**: Each test should be independent
2. **Descriptive Names**: Clearly describe what's being tested
3. **AAA Pattern**: Arrange, Act, Assert
4. **Minimal Fixtures**: Only set up what's necessary
5. **Test Edge Cases**: Include boundary conditions

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/unit/test_voice.py
```

### Run Specific Test Function
```bash
pytest tests/unit/test_voice.py::test_voice_recognition
```

### With Coverage Report
```bash
pytest --cov=modules tests/
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

```python
import pytest
from modules.voice import VoiceAssistant

@pytest.fixture
def voice_assistant():
    """Create a VoiceAssistant instance for testing."""
    va = VoiceAssistant()
    yield va
    va.cleanup()
```

## Mocking

Use `unittest.mock` to isolate units:

```python
from unittest.mock import patch

def test_voice_activation(mock_recognizer):
    with patch('speech_recognition.Recognizer') as mock_rec:
        va = VoiceAssistant()
        # Test voice activation
```

## Continuous Integration

Tests are automatically run on push via GitHub Actions. See `.github/workflows/tests.yml`.

## Code Coverage

Aim for at least 80% code coverage. Current coverage:

```
----------- coverage: platform win32 -----------
Name                          Stmts   Miss  Cover
-------------------------------------------------
modules/__init__.py               0      0   100%
modules/character.py             45      5    89%
modules/voice.py                 98     12    88%
modules/video_player.py          32      4    88%
-------------------------------------------------
TOTAL                           175     21    88%
```

## Debugging Tests

### Run with PDB
```bash
pytest --pdb
```

### Verbose Output
```bash
pytest -v
```

### Show All Output
```bash
pytest -s
```

## Best Practices

1. **Fast**: Tests should run quickly
2. **Deterministic**: Same input → same output
3. **Isolated**: No test depends on another
4. **Readable**: Clear test names and assertions
5. **Maintainable**: Easy to update with code changes
