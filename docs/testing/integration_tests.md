# Integration Testing

This document outlines the procedures for testing how different modules of the MAYA AI Chatbot work together.

## Test Categories

### 1. Voice and Character Integration
- **Description**: Verify voice synthesis works with character traits
- **Test Cases**:
  - Switch between different character traits and verify voice changes
  - Test custom trait creation and application
  - Verify persistence of voice settings

### 2. Video and Voice Integration
- **Description**: Test video playback during voice interactions
- **Test Cases**:
  - Video appears when bot speaks in voice mode
  - Video stops when voice stops
  - Multiple sequential voice commands

### 3. UI and Backend Integration
- **Description**: Test UI controls affect backend behavior
- **Test Cases**:
  - Toggle between text/voice modes
  - Adjust voice parameters through UI
  - Test all settings persistence

## Test Environment

### Prerequisites
- Python 3.8+
- All project dependencies
- Test video files in `resources/videos/`
- Microphone and speakers/headphones

### Setup
1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

2. Prepare test data:
   ```bash
   mkdir -p resources/videos
   # Add test video files
   ```

## Running Tests

### Run All Integration Tests
```bash
pytest tests/integration/
```

### Run Specific Test Module
```bash
pytest tests/integration/test_voice_character_integration.py
```

### With Coverage
```bash
pytest --cov=modules tests/integration/
```

## Test Data

### Sample Test Cases
```yaml
- name: Tsundere Character Test
  steps:
    - action: Set character to Tsundere
    - action: Send message "Hello"
    - expect: Response contains tsundere-style text
    - expect: Voice pitch is higher

- name: Video Playback Test
  steps:
    - action: Enable voice mode
    - action: Send message "Tell me a joke"
    - expect: Video plays during response
    - expect: Video stops after response completes
```

## Common Integration Issues

1. **Timing Issues**
   - Add appropriate waits in tests
   - Use event-based signaling when possible

2. **State Management**
   - Ensure proper cleanup between tests
   - Reset application state before each test

3. **Resource Contention**
   - Avoid simultaneous access to shared resources
   - Use locks or test isolation

## Performance Testing

### Response Time
- Voice recognition: < 2 seconds
- Text-to-speech: < 1 second
- Video startup: < 500ms

### Resource Usage
- Memory: < 200MB for typical usage
- CPU: < 30% during voice processing

## Security Testing

### Input Validation
- Test with malformed input
- Verify proper error handling
- Check for injection vulnerabilities

### Data Privacy
- No sensitive data in logs
- Proper handling of voice recordings
- Secure storage of settings

## Test Automation

### CI/CD Pipeline
Tests are automatically run on push via GitHub Actions. See `.github/workflows/tests.yml`.

### Scheduled Testing
Nightly test runs check for:
- Performance regressions
- Integration issues
- Dependency updates

## Test Reporting

### Test Results
- JUnit XML format: `test-results.xml`
- HTML coverage report: `htmlcov/`

### Metrics
- Test coverage percentage
- Pass/fail rates
- Performance benchmarks

## Maintenance

### Test Updates
- Update tests when adding new features
- Remove or update obsolete tests
- Keep test data current

### Documentation
- Keep test cases up to date
- Document new test procedures
- Update known issues
