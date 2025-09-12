# YTLite Technical Specifications

## Overview
YTLite is a comprehensive YouTube content automation system that transforms markdown content into multimedia presentations with SVG packaging, automated validation, and web-based management.

## System Architecture

### Core Components

#### 1. Content Processing Pipeline
- **Content Parser** (`content_parser.py`): Processes markdown files with YAML frontmatter
- **Audio Generator** (`audio_generator.py`): Text-to-speech conversion using Azure Cognitive Services
- **Video Generator** (`video_generator.py`): Creates video from images, audio, and transitions
- **SVG Packager** (`svg_packager.py`): Generates interactive SVG containers with embedded media

#### 2. Validation System
- **SVG Validator** (`svg_validator.py`): Comprehensive XML validation and auto-repair
- **Decorators**: `@svg_validation_wrapper` for automatic validation
- **Context Managers**: `SVGOperationManager` for safe editing operations
- **Batch Processing**: Project-wide validation and fixing

#### 3. Web Interface
- **Web GUI** (`web_gui.py`): Flask-based management interface
- **REST API**: Complete project management via HTTP endpoints
- **Real-time Progress**: WebSocket-style progress tracking
- **Theme Support**: Day/night mode with CSS variables

#### 4. Storage & Versioning
- **Project Structure**: Organized output directory with versioning
- **Version Control**: Automatic backup before SVG modifications
- **File Serving**: Secure file access with path traversal protection

## API Specifications

### REST Endpoints

#### Project Management
```
GET  /api/projects              # List all projects with metadata
POST /api/generate              # Create new project from form data
POST /api/delete_project        # Delete project with confirmation
```

#### SVG Operations
```
GET  /api/validate_svg          # Validate specific project SVGs
GET  /api/svg_meta             # Extract SVG metadata
POST /api/update_svg_media     # Update embedded media content
```

#### Version Control
```
GET  /api/project_history      # Get version history for project
POST /api/restore_version      # Restore specific version
```

#### External Integrations
```
POST /api/publish_wordpress    # Publish to WordPress
POST /api/fetch_nextcloud      # Import from Nextcloud
```

### Data Models

#### Project Structure
```
output/projects/{project_name}/
├── {project_name}.svg          # Main SVG package
├── {project_name}.mp4          # Generated video
├── {project_name}.mp3          # Generated audio
├── thumbnail.jpg               # Video thumbnail
├── .env                        # Project-specific config
├── metadata.json               # Project metadata
└── versions/                   # Version history
    ├── {project_name}_v1.svg
    ├── {project_name}_v2.svg
    └── ...
```

#### SVG Package Format
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080">
  <!-- Metadata -->
  <metadata>
    <title>Project Title</title>
    <date>2025-01-12</date>
    <theme>tech</theme>
    <voice>en-US-AriaNeural</voice>
  </metadata>
  
  <!-- Content layers -->
  <g id="background">...</g>
  <g id="content">...</g>
  
  <!-- Embedded media -->
  <video controls="controls" width="1920" height="1080">
    <source src="video.mp4" type="video/mp4"/>
  </video>
  
  <audio controls="controls">
    <source src="audio.mp3" type="audio/mpeg"/>
  </audio>
</svg>
```

## Validation System

### XML Compliance
- **xmllint Integration**: Primary validation using system xmllint
- **Fallback Validation**: Basic XML parsing when xmllint unavailable
- **Auto-fix Capabilities**: Common issues like boolean attributes

### Validation Workflow
1. **Pre-generation**: Validate templates and content
2. **Post-generation**: Automatic validation with fix attempts
3. **Post-edit**: Validation after any SVG modification
4. **Batch Operations**: Project-wide validation and reporting

### Supported Auto-fixes
- Boolean attributes without values (`controls` → `controls="controls"`)
- Unclosed tags and malformed XML structures
- Invalid character entities
- Namespace corrections

## Security Considerations

### Path Traversal Protection
```python
# Security check example
if not str(project_dir.resolve()).startswith(str((OUTPUT_DIR / 'projects').resolve())):
    return jsonify({'message': 'Invalid project path'}), 400
```

### Input Validation
- Project names: Alphanumeric with limited special characters
- File uploads: Size limits and type validation
- Path parameters: Strict validation against directory traversal

### File Access Control
- Restricted file serving from output directory only
- No direct filesystem access via API
- Secure temporary file handling

## Performance Specifications

### Generation Performance
- **Target**: <30 seconds for standard project (1-3 minutes content)
- **Factors**: TTS speed, video encoding, SVG complexity
- **Optimization**: Parallel processing where possible

### Validation Performance
- **Single SVG**: <1 second validation + fix
- **Bulk validation**: <5 seconds for 10 files
- **Memory usage**: <100MB for typical project

### Web Interface
- **Load time**: <2 seconds for project list
- **File serving**: Direct nginx-style serving
- **Progress updates**: 500ms polling interval

## Configuration Management

### Environment Variables
```bash
OUTPUT_DIR=/path/to/output      # Output directory
FLASK_PORT=5000                 # Web GUI port
YTLITE_FAST_TEST=1             # Skip heavy operations in tests
AZURE_SPEECH_KEY=xxx           # TTS service key
AZURE_SPEECH_REGION=xxx        # TTS service region
```

### Project-specific Configuration
```bash
# .env file in project directory
WP_URL=https://example.com
WP_USERNAME=user
WP_PASSWORD=pass
NEXTCLOUD_URL=https://cloud.example.com
NEXTCLOUD_USER=user
NEXTCLOUD_PASS=pass
```

## Error Handling

### Validation Errors
- **Graceful degradation**: Continue with warnings for non-critical issues
- **User feedback**: Clear error messages in Web GUI
- **Logging**: Comprehensive error logging with context

### Generation Failures
- **Partial recovery**: Save intermediate results
- **Progress preservation**: Resume from last successful step
- **Cleanup**: Automatic cleanup of failed generation artifacts

## Testing Strategy

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API endpoint testing
3. **End-to-End Tests**: Complete workflow validation
4. **Performance Tests**: Load and timing validation
5. **Security Tests**: Vulnerability scanning

### Test Coverage Requirements
- **Core Functions**: >90% coverage
- **API Endpoints**: 100% endpoint coverage
- **Error Paths**: All error conditions tested
- **Security**: All input validation paths

## Deployment Specifications

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8+
- **Dependencies**: ffmpeg, xmllint, imagemagick
- **Disk Space**: 1GB+ for dependencies, variable for projects
- **Memory**: 2GB+ recommended

### Docker Support
```yaml
version: '3.8'
services:
  ytlite-app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./output:/app/output
    environment:
      - OUTPUT_DIR=/app/output
```

### Production Considerations
- **Reverse Proxy**: nginx for static file serving
- **Process Management**: systemd or supervisor
- **Monitoring**: Log aggregation and metrics
- **Backup**: Regular output directory backups

## Future Extensibility

### Plugin Architecture
- **Voice Providers**: Modular TTS backend support
- **Themes**: CSS-based theme system
- **Templates**: Configurable SVG templates
- **Validation Rules**: Extensible validation framework

### API Versioning
- **URL Versioning**: `/api/v1/`, `/api/v2/`
- **Backward Compatibility**: Maintain older API versions
- **Feature Flags**: Gradual feature rollout

This specification serves as the authoritative technical reference for YTLite system architecture, implementation details, and operational requirements.
