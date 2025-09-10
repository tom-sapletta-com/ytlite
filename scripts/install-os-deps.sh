#!/bin/bash
# Universal OS dependency installer

# Exit immediately if a command exits with a non-zero status.
set -e

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

# --- Helper Functions ---
echo_info() {
    echo -e "${YELLOW}INFO: $1${NC}"
}

echo_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

echo_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

# --- Dependency Installation ---
install_deps() {
    PACKAGE_MANAGER=""
    INSTALL_CMD=""
    PACKAGES="ffmpeg"

    # Detect package manager
    if command -v apt-get &> /dev/null; then
        PACKAGE_MANAGER="apt-get"
        INSTALL_CMD="sudo apt-get install -y"
        UPDATE_CMD="sudo apt-get update"
    elif command -v yum &> /dev/null; then
        PACKAGE_MANAGER="yum"
        INSTALL_CMD="sudo yum install -y"
    elif command -v dnf &> /dev/null; then
        PACKAGE_MANAGER="dnf"
        INSTALL_CMD="sudo dnf install -y"
    elif command -v pacman &> /dev/null; then
        PACKAGE_MANAGER="pacman"
        INSTALL_CMD="sudo pacman -S --noconfirm"
    elif command -v brew &> /dev/null; then
        PACKAGE_MANAGER="brew"
        INSTALL_CMD="brew install"
    else
        echo_error "Unsupported package manager. Please install 'ffmpeg' manually."
        exit 1
    fi

    echo_info "Using '$PACKAGE_MANAGER' to install dependencies: $PACKAGES"

    # Check if ffmpeg is already installed
    if command -v ffmpeg &> /dev/null; then
        echo_success "'ffmpeg' is already installed."
        return 0
    fi

    # Update and install
    if [ -n "$UPDATE_CMD" ]; then
        echo_info "Updating package lists..."
        $UPDATE_CMD
    fi

    echo_info "Installing '$PACKAGES'... (This may require your password)"
    $INSTALL_CMD $PACKAGES

    echo_success "Dependencies installed successfully."
}

# --- Main Execution ---
main() {
    echo_info "Starting OS dependency check..."
    install_deps
    echo_success "All OS dependencies are satisfied."
}

main
