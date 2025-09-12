#!/bin/bash
# YTLite Test Data Validation Script
# Checks project folders and tests media and SVG files for errors
# Removes corrupted files and generates validation report

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$BASE_DIR/output"
PROJECTS_DIR="$OUTPUT_DIR/projects"
SVG_PROJECTS_DIR="$OUTPUT_DIR/svg_projects"
LOG_FILE="$OUTPUT_DIR/test_data_validation.log"
REPORT_FILE="$OUTPUT_DIR/test_data_report.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_FILES=0
VALID_FILES=0
CORRUPTED_FILES=0
REMOVED_FILES=0

# Arrays to store results
declare -a VALID_PROJECTS=()
declare -a CORRUPTED_PROJECTS=()
declare -a REMOVED_FILES_LIST=()

echo_log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_only() {
    echo "$1" >> "$LOG_FILE"
}

validate_video_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    echo_log "${BLUE}  Validating video: $filename${NC}"
    
    # Check if file exists and has content
    if [[ ! -f "$file" || ! -s "$file" ]]; then
        echo_log "${RED}    ❌ File is empty or missing${NC}"
        return 1
    fi
    
    # Use ffprobe to validate video file
    if command -v ffprobe >/dev/null 2>&1; then
        if ffprobe -v quiet -show_format -show_streams "$file" >/dev/null 2>&1; then
            # Get video duration and basic info
            duration=$(ffprobe -v quiet -show_entries format=duration -of csv="p=0" "$file" 2>/dev/null || echo "unknown")
            codec=$(ffprobe -v quiet -show_entries stream=codec_name -select_streams v:0 -of csv="p=0" "$file" 2>/dev/null || echo "unknown")
            
            echo_log "${GREEN}    ✅ Valid video - Duration: ${duration}s, Codec: $codec${NC}"
            log_only "VALID_VIDEO: $file, duration=$duration, codec=$codec"
            return 0
        else
            echo_log "${RED}    ❌ Corrupted video file${NC}"
            log_only "CORRUPTED_VIDEO: $file, reason=ffprobe_failed"
            return 1
        fi
    else
        # Fallback: basic file type check
        if file "$file" | grep -q -i "video\|mp4\|webm\|avi\|mov"; then
            echo_log "${GREEN}    ✅ Video file (basic check)${NC}"
            log_only "VALID_VIDEO: $file, check=basic_only"
            return 0
        else
            echo_log "${RED}    ❌ Not a valid video file${NC}"
            log_only "CORRUPTED_VIDEO: $file, reason=invalid_format"
            return 1
        fi
    fi
}

validate_audio_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    echo_log "${BLUE}  Validating audio: $filename${NC}"
    
    # Check if file exists and has content
    if [[ ! -f "$file" || ! -s "$file" ]]; then
        echo_log "${RED}    ❌ File is empty or missing${NC}"
        return 1
    fi
    
    # Use ffprobe to validate audio file
    if command -v ffprobe >/dev/null 2>&1; then
        if ffprobe -v quiet -show_format -show_streams "$file" >/dev/null 2>&1; then
            # Get audio duration and basic info
            duration=$(ffprobe -v quiet -show_entries format=duration -of csv="p=0" "$file" 2>/dev/null || echo "unknown")
            codec=$(ffprobe -v quiet -show_entries stream=codec_name -select_streams a:0 -of csv="p=0" "$file" 2>/dev/null || echo "unknown")
            
            echo_log "${GREEN}    ✅ Valid audio - Duration: ${duration}s, Codec: $codec${NC}"
            log_only "VALID_AUDIO: $file, duration=$duration, codec=$codec"
            return 0
        else
            echo_log "${RED}    ❌ Corrupted audio file${NC}"
            log_only "CORRUPTED_AUDIO: $file, reason=ffprobe_failed"
            return 1
        fi
    else
        # Fallback: basic file type check
        if file "$file" | grep -q -i "audio\|mp3\|wav\|m4a\|ogg"; then
            echo_log "${GREEN}    ✅ Audio file (basic check)${NC}"
            log_only "VALID_AUDIO: $file, check=basic_only"
            return 0
        else
            echo_log "${RED}    ❌ Not a valid audio file${NC}"
            log_only "CORRUPTED_AUDIO: $file, reason=invalid_format"
            return 1
        fi
    fi
}

validate_svg_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    echo_log "${BLUE}  Validating SVG: $filename${NC}"
    
    # Check if file exists and has content
    if [[ ! -f "$file" || ! -s "$file" ]]; then
        echo_log "${RED}    ❌ File is empty or missing${NC}"
        return 1
    fi
    
    # Basic SVG validation
    if ! grep -q "<svg" "$file"; then
        echo_log "${RED}    ❌ Missing SVG root element${NC}"
        log_only "CORRUPTED_SVG: $file, reason=no_svg_element"
        return 1
    fi
    
    # Check for well-formed XML
    if command -v xmllint >/dev/null 2>&1; then
        if xmllint --noout "$file" 2>/dev/null; then
            echo_log "${GREEN}    ✅ Valid SVG (XML well-formed)${NC}"
            
            # Check for embedded media
            data_uris=$(grep -c "data:" "$file" 2>/dev/null || echo "0")
            if [[ "$data_uris" -gt 0 ]]; then
                echo_log "      📎 Contains $data_uris data URI(s)"
                log_only "VALID_SVG: $file, data_uris=$data_uris"
            else
                log_only "VALID_SVG: $file, data_uris=0"
            fi
            return 0
        else
            echo_log "${RED}    ❌ Malformed XML in SVG${NC}"
            log_only "CORRUPTED_SVG: $file, reason=malformed_xml"
            return 1
        fi
    else
        # Basic validation without xmllint
        if grep -q "</svg>" "$file"; then
            echo_log "${GREEN}    ✅ SVG file (basic check)${NC}"
            log_only "VALID_SVG: $file, check=basic_only"
            return 0
        else
            echo_log "${RED}    ❌ Incomplete SVG file${NC}"
            log_only "CORRUPTED_SVG: $file, reason=incomplete"
            return 1
        fi
    fi
}

remove_corrupted_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    echo_log "${YELLOW}  Removing corrupted file: $filename${NC}"
    
    if rm "$file" 2>/dev/null; then
        echo_log "${GREEN}    ✅ Successfully removed${NC}"
        REMOVED_FILES_LIST+=("$file")
        ((REMOVED_FILES++))
        log_only "REMOVED: $file"
    else
        echo_log "${RED}    ❌ Failed to remove file${NC}"
        log_only "FAILED_REMOVE: $file"
    fi
}

validate_project_directory() {
    local project_dir="$1"
    local project_name=$(basename "$project_dir")
    
    echo_log "\n${BLUE}🔍 Validating project: $project_name${NC}"
    
    local project_valid=true
    local files_in_project=0
    local valid_files_in_project=0
    
    # Find and validate video files
    while IFS= read -r -d '' file; do
        ((files_in_project++))
        ((TOTAL_FILES++))
        
        if validate_video_file "$file"; then
            ((valid_files_in_project++))
            ((VALID_FILES++))
        else
            project_valid=false
            ((CORRUPTED_FILES++))
            remove_corrupted_file "$file"
        fi
    done < <(find "$project_dir" -type f \( -iname "*.mp4" -o -iname "*.webm" -o -iname "*.avi" -o -iname "*.mov" \) -print0 2>/dev/null || true)
    
    # Find and validate audio files
    while IFS= read -r -d '' file; do
        ((files_in_project++))
        ((TOTAL_FILES++))
        
        if validate_audio_file "$file"; then
            ((valid_files_in_project++))
            ((VALID_FILES++))
        else
            project_valid=false
            ((CORRUPTED_FILES++))
            remove_corrupted_file "$file"
        fi
    done < <(find "$project_dir" -type f \( -iname "*.mp3" -o -iname "*.wav" -o -iname "*.m4a" -o -iname "*.ogg" \) -print0 2>/dev/null || true)
    
    # Find and validate SVG files
    while IFS= read -r -d '' file; do
        ((files_in_project++))
        ((TOTAL_FILES++))
        
        if validate_svg_file "$file"; then
            ((valid_files_in_project++))
            ((VALID_FILES++))
        else
            project_valid=false
            ((CORRUPTED_FILES++))
            remove_corrupted_file "$file"
        fi
    done < <(find "$project_dir" -type f -iname "*.svg" -print0 2>/dev/null || true)
    
    # Summarize project validation
    if [[ "$project_valid" == true ]]; then
        echo_log "${GREEN}✅ Project '$project_name' - All $files_in_project file(s) valid${NC}"
        VALID_PROJECTS+=("$project_name")
    else
        echo_log "${YELLOW}⚠️  Project '$project_name' - $valid_files_in_project/$files_in_project files valid${NC}"
        CORRUPTED_PROJECTS+=("$project_name")
    fi
}

validate_svg_project() {
    local svg_file="$1"
    local project_name=$(basename "$svg_file" .svg)
    
    echo_log "\n${BLUE}🔍 Validating SVG project: $project_name${NC}"
    
    ((TOTAL_FILES++))
    
    if validate_svg_file "$svg_file"; then
        ((VALID_FILES++))
        echo_log "${GREEN}✅ SVG Project '$project_name' - Valid${NC}"
        VALID_PROJECTS+=("$project_name (SVG)")
    else
        ((CORRUPTED_FILES++))
        echo_log "${YELLOW}⚠️  SVG Project '$project_name' - Corrupted${NC}"
        CORRUPTED_PROJECTS+=("$project_name (SVG)")
        remove_corrupted_file "$svg_file"
    fi
}

generate_report() {
    local end_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Generate JSON report
    cat > "$REPORT_FILE" << EOF
{
  "validation_report": {
    "timestamp": "$end_time",
    "summary": {
      "total_files": $TOTAL_FILES,
      "valid_files": $VALID_FILES,
      "corrupted_files": $CORRUPTED_FILES,
      "removed_files": $REMOVED_FILES,
      "total_projects": $((${#VALID_PROJECTS[@]} + ${#CORRUPTED_PROJECTS[@]})),
      "valid_projects": ${#VALID_PROJECTS[@]},
      "corrupted_projects": ${#CORRUPTED_PROJECTS[@]}
    },
    "valid_projects": [$(printf '"%s",' "${VALID_PROJECTS[@]}" | sed 's/,$//')]",
    "corrupted_projects": [$(printf '"%s",' "${CORRUPTED_PROJECTS[@]}" | sed 's/,$//')]",
    "removed_files": [$(printf '"%s",' "${REMOVED_FILES_LIST[@]}" | sed 's/,$//')]"
  }
}
EOF

    echo_log "\n${GREEN}📊 Validation Summary:${NC}"
    echo_log "  Total files processed: $TOTAL_FILES"
    echo_log "  Valid files: $VALID_FILES"
    echo_log "  Corrupted files: $CORRUPTED_FILES"
    echo_log "  Removed files: $REMOVED_FILES"
    echo_log "  Valid projects: ${#VALID_PROJECTS[@]}"
    echo_log "  Projects with issues: ${#CORRUPTED_PROJECTS[@]}"
    echo_log "\n${BLUE}📋 Report saved to: $REPORT_FILE${NC}"
    echo_log "${BLUE}📋 Detailed log: $LOG_FILE${NC}"
}

main() {
    local start_time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    echo_log "${GREEN}🚀 YTLite Test Data Validation Started${NC}"
    echo_log "Start time: $start_time"
    echo_log "Output directory: $OUTPUT_DIR"
    
    # Clear previous log
    > "$LOG_FILE"
    
    # Create output directories if they don't exist
    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$PROJECTS_DIR"
    mkdir -p "$SVG_PROJECTS_DIR"
    
    # Validate directory-based projects
    if [[ -d "$PROJECTS_DIR" ]]; then
        echo_log "\n${BLUE}📁 Scanning directory projects...${NC}"
        
        for project_dir in "$PROJECTS_DIR"/*; do
            if [[ -d "$project_dir" ]]; then
                validate_project_directory "$project_dir"
            fi
        done
    else
        echo_log "${YELLOW}⚠️  No projects directory found${NC}"
    fi
    
    # Validate SVG-based projects
    if [[ -d "$SVG_PROJECTS_DIR" ]]; then
        echo_log "\n${BLUE}📄 Scanning SVG projects...${NC}"
        
        for svg_file in "$SVG_PROJECTS_DIR"/*.svg; do
            if [[ -f "$svg_file" ]]; then
                validate_svg_project "$svg_file"
            fi
        done
    else
        echo_log "${YELLOW}⚠️  No SVG projects directory found${NC}"
    fi
    
    # Generate final report
    generate_report
    
    # Return appropriate exit code
    if [[ $CORRUPTED_FILES -eq 0 ]]; then
        echo_log "\n${GREEN}🎉 All files are valid! No issues found.${NC}"
        exit 0
    else
        echo_log "\n${YELLOW}⚠️  Found and cleaned $CORRUPTED_FILES corrupted file(s).${NC}"
        exit 1
    fi
}

# Check if help is requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "YTLite Test Data Validation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "This script validates all media and SVG files in the YTLite output directory."
    echo "It checks for corrupted files and removes them automatically."
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "The script will:"
    echo "  1. Scan all project directories for media files"
    echo "  2. Validate SVG, video, and audio files"
    echo "  3. Remove any corrupted files found"
    echo "  4. Generate a detailed validation report"
    echo ""
    echo "Output files:"
    echo "  - $OUTPUT_DIR/test_data_validation.log"
    echo "  - $OUTPUT_DIR/test_data_report.json"
    exit 0
fi

# Run main function
main "$@"
