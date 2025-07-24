# Character Module Testing

This document outlines the testing procedures for the anime character system, including trait management, voice customization, and response formatting.

## Test Cases

### 1. Character Trait Selection
- **Description**: Test selecting different character traits
- **Steps**:
  1. Go to `Settings > Character Settings`
  2. Select different character types from the dropdown
  3. Click "Preview Voice" for each
- **Expected**: Voice and text style should match the selected character

### 2. Custom Trait Creation
- **Description**: Create and test a custom character trait
- **Steps**:
  1. Open Character Settings
  2. Select a base character
  3. Modify name, description, pitch, and speed
  4. Click "Save" and test with a message
- **Expected**: New trait should be saved and applied

### 3. Trait Persistence
- **Description**: Verify traits persist between sessions
- **Steps**:
  1. Create/select a character trait
  2. Close and reopen the application
  3. Check Character Settings
- **Expected**: Previous trait selection should be remembered

## Test Data

### Sample Character Traits
```json
{
  "tsundere": {
    "name": "Tsundere",
    "description": "Acts cold but has a warm heart",
    "pitch_modifier": 0.5,
    "speed_modifier": 1.2,
    "response_style": "tsundere"
  }
}
```

## Common Issues

1. **Trait Not Saving**
   - Check write permissions for config directory
   - Verify JSON syntax in saved file
   
2. **Voice Doesn't Match Trait**
   - Verify TTS engine supports pitch/speed changes
   - Check system audio settings

## Test Coverage

| Feature | Tested | Notes |
|---------|--------|-------|
| Trait Selection | ✅ | UI and application |
| Custom Traits | ✅ | Creation and modification |
| Trait Persistence | ✅ | Across sessions |
| Voice Customization | ✅ | Pitch and speed |
| Response Formatting | ✅ | Style application |

## Automation

Run character tests with:
```bash
pytest tests/character/test_character_system.py -v
```

## Performance
- Trait switching should be instantaneous
- No noticeable delay when applying custom traits

## Security
- Character trait files should be validated
- No executable code should be allowed in trait definitions
