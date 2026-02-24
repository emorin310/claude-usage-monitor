#!/usr/bin/env bash
# install.sh - Install injection shield to a workspace
#
# Usage:
#   ./install.sh                     # Install to current workspace (pwd or ~/clawd-*)
#   ./install.sh /path/to/workspace  # Install to specific workspace
#
# What it does:
#   1. Copies scripts to workspace/scripts/
#   2. Copies prompt prefix to workspace/prompts/
#   3. Creates logs directory
#   4. Makes scripts executable
#   5. Creates symlinks for easy access (optional)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}!${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

# Determine target workspace
if [ $# -ge 1 ]; then
    WORKSPACE="$1"
else
    # Try to find workspace automatically
    if [ -f "./AGENTS.md" ] || [ -f "./SOUL.md" ]; then
        WORKSPACE="$(pwd)"
    elif ls -d ~/clawd-* 2>/dev/null | head -1 | grep -q .; then
        WORKSPACE=$(ls -d ~/clawd-* 2>/dev/null | head -1)
    elif ls -d ~/clawdbot-* 2>/dev/null | head -1 | grep -q .; then
        WORKSPACE=$(ls -d ~/clawdbot-* 2>/dev/null | head -1)
    else
        WORKSPACE="$(pwd)"
    fi
fi

echo "Installing Injection Shield to: $WORKSPACE"
echo ""

# Verify source files exist
if [ ! -f "${SKILL_DIR}/scripts/sanitize.sh" ]; then
    print_error "Source scripts not found in ${SKILL_DIR}/scripts/"
    exit 1
fi

# Create directories
mkdir -p "${WORKSPACE}/scripts" 2>/dev/null && print_success "Created scripts/" || print_warning "scripts/ already exists"
mkdir -p "${WORKSPACE}/prompts" 2>/dev/null && print_success "Created prompts/" || print_warning "prompts/ already exists"
mkdir -p "${WORKSPACE}/logs" 2>/dev/null && print_success "Created logs/" || print_warning "logs/ already exists"

# Copy scripts
cp "${SKILL_DIR}/scripts/sanitize.sh" "${WORKSPACE}/scripts/"
print_success "Copied sanitize.sh"

cp "${SKILL_DIR}/scripts/safe-fetch.sh" "${WORKSPACE}/scripts/"
print_success "Copied safe-fetch.sh"

cp "${SKILL_DIR}/scripts/cron-wrapper.sh" "${WORKSPACE}/scripts/"
print_success "Copied cron-wrapper.sh"

# Copy prompt prefix
cp "${SKILL_DIR}/prompts/anti-injection-prefix.txt" "${WORKSPACE}/prompts/"
print_success "Copied anti-injection-prefix.txt"

# Make scripts executable
chmod +x "${WORKSPACE}/scripts/sanitize.sh"
chmod +x "${WORKSPACE}/scripts/safe-fetch.sh"
chmod +x "${WORKSPACE}/scripts/cron-wrapper.sh"
print_success "Made scripts executable"

# Copy SKILL.md for reference
if [ -f "${SKILL_DIR}/SKILL.md" ]; then
    mkdir -p "${WORKSPACE}/skills/injection-shield" 2>/dev/null || true
    cp "${SKILL_DIR}/SKILL.md" "${WORKSPACE}/skills/injection-shield/"
    print_success "Copied SKILL.md for reference"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Usage examples:"
echo "  # Sanitize any content"
echo "  echo \"\$content\" | ${WORKSPACE}/scripts/sanitize.sh"
echo ""
echo "  # Wrap a command that fetches external data"
echo "  ${WORKSPACE}/scripts/safe-fetch.sh curl -s https://api.example.com"
echo ""
echo "  # Wrap a cron job (includes anti-injection prefix)"
echo "  ${WORKSPACE}/scripts/cron-wrapper.sh ./my-email-checker.sh"
echo ""
echo "Logs will be written to: ${WORKSPACE}/logs/"
