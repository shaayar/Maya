# Video Playback Testing

This document outlines the testing procedures for the video playback features in MAYA AI Chatbot, including video display during voice mode and related functionality.

## Test Cases

### 1. Basic Video Playback
- **Description**: Test video plays during voice mode
- **Prerequisites**: 
  - Place a test video file in `resources/videos/`
  - Supported formats: MP4, WebM, MOV
- **Steps**:
  1. Start voice mode (click mic or say "Hey Maya")
  2. Speak a command
- **Expected**: Video should play in a floating window while the bot speaks

### 2. Video Window Controls
- **Description**: Test video player controls
- **Steps**:
  1. Start voice mode to show video
  2. Test close button (X)
  3. Test window dragging
- **Expected**:
  - Close button should hide the video
  - Window should be draggable

### 3. Multiple Videos
- **Description**: Test with multiple video files
- **Steps**:
  1. Place multiple video files in `resources/videos/`
  2. Test voice mode multiple times
- **Expected**: Should handle multiple video files correctly

## Test Data

### Supported Video Formats
- MP4 (H.264 codec recommended)
- WebM (VP8/VP9)
- MOV (H.264)

### Sample Test Videos
- Short clip (5-10 seconds recommended)
- Resolution: 480p or 720p
- File size: Under 10MB

## Common Issues

1. **Video Doesn't Play**
   - Check file format and codec
   - Verify file permissions
   - Ensure file is in `resources/videos/`
   
2. **Audio/Video Sync**
   - Check video encoding
   - Test with different video files

3. **Performance Issues**
   - Reduce video resolution
   - Lower bitrate
   - Use shorter clips

## Test Coverage

| Feature | Tested | Notes |
|---------|--------|-------|
| Video Playback | ✅ | Basic functionality |
| Multiple Videos | ✅ | File handling |
| Window Controls | ✅ | Close, drag |
| Format Support | ✅ | MP4, WebM, MOV |
| Performance | ✅ | Resource usage |

## Automation

Run video tests with:
```bash
pytest tests/video/test_video_playback.py -v
```

## Performance
- Video should start within 1 second
- CPU usage should remain reasonable
- Memory should be properly released after closing

## Security
- Validate video file paths
- Sanitize file names
- Handle corrupted video files gracefully
