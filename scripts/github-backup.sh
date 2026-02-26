#!/bin/bash
# GitHub backup script for OpenClaw - runs at 4:30am daily

set -e

LOG_FILE="/home/magi/clawd/logs/backup.log"
BACKUP_DIR="/home/magi/clawd-backup"
REPO_URL="git@github.com:emorin310/magi-backup.git"

mkdir -p "$(dirname "$LOG_FILE")"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting GitHub backup process..."

# Create/update backup directory
if [ ! -d "$BACKUP_DIR" ]; then
    log "Cloning backup repository..."
    git clone "$REPO_URL" "$BACKUP_DIR" || {
        log "❌ Failed to clone backup repository"
        exit 1
    }
else
    log "Updating backup repository..."
    cd "$BACKUP_DIR"
    git pull origin main || {
        log "❌ Failed to pull latest changes"
        exit 1
    }
fi

cd "$BACKUP_DIR"

# Clear previous backup
log "Clearing previous backup files..."
find . -name "*.md" -not -path "./.git/*" -delete
find . -name "*.json" -not -path "./.git/*" -delete
find . -name "*.sh" -not -path "./.git/*" -delete
find . -name "*.yml" -not -path "./.git/*" -delete
find . -name "*.yaml" -not -path "./.git/*" -delete

# Copy critical files
log "Copying workspace files..."
cp /home/magi/clawd/SOUL.md . 2>/dev/null || log "Warning: SOUL.md not found"
cp /home/magi/clawd/MEMORY.md . 2>/dev/null || log "Warning: MEMORY.md not found"
cp /home/magi/clawd/USER.md . 2>/dev/null || log "Warning: USER.md not found"
cp /home/magi/clawd/IDENTITY.md . 2>/dev/null || log "Warning: IDENTITY.md not found"
cp /home/magi/clawd/TOOLS.md . 2>/dev/null || log "Warning: TOOLS.md not found"
cp /home/magi/clawd/AGENTS.md . 2>/dev/null || log "Warning: AGENTS.md not found"
cp /home/magi/clawd/HEARTBEAT.md . 2>/dev/null || log "Warning: HEARTBEAT.md not found"

# Copy memory directory
log "Copying memory files..."
mkdir -p memory
cp -r /home/magi/clawd/memory/* memory/ 2>/dev/null || log "Warning: No memory files found"

# Copy scripts
log "Copying scripts..."
mkdir -p scripts
cp -r /home/magi/clawd/scripts/* scripts/ 2>/dev/null || log "Warning: No scripts found"

# Copy skills directory
log "Copying skills..."
mkdir -p skills
cp -r /home/magi/clawd/skills/* skills/ 2>/dev/null || log "Warning: No skills found"

# Copy cron configuration
log "Copying cron jobs..."
crontab -l > crontab.txt 2>/dev/null || echo "# No crontab found" > crontab.txt

# Copy OpenClaw config
log "Copying OpenClaw config..."
cp ~/.openclaw/config.yaml openclaw-config.yaml 2>/dev/null || log "Warning: OpenClaw config not found"

# Scan for secrets and sanitize
log "Scanning for secrets and sanitizing..."

# Define secret patterns
declare -a SECRET_PATTERNS=(
    "sk-[a-zA-Z0-9_-]{20,}"                    # OpenAI API keys
    "xoxb-[0-9]+-[0-9]+-[0-9]+-[a-zA-Z0-9]+"  # Slack tokens
    "ghp_[a-zA-Z0-9]{36}"                      # GitHub personal access tokens
    "gho_[a-zA-Z0-9]{36}"                      # GitHub OAuth tokens
    "[0-9]+-[a-zA-Z0-9_-]{32,}"               # Discord tokens
    "AIza[0-9A-Za-z_-]{35}"                   # Google API keys
    "[a-f0-9]{64}"                            # Generic 64-char hex tokens
    "password[[:space:]]*[:=][[:space:]]*['\"]?[^'\"[:space:]]+['\"]?"  # Password fields
    "token[[:space:]]*[:=][[:space:]]*['\"]?[^'\"[:space:]]+['\"]?"     # Token fields
    "api_key[[:space:]]*[:=][[:space:]]*['\"]?[^'\"[:space:]]+['\"]?"   # API key fields
)

# Sanitization replacements
declare -A REPLACEMENTS=(
    ["sk-[a-zA-Z0-9_-]{20,}"]="[OPENAI_API_KEY]"
    ["xoxb-[0-9]+-[0-9]+-[0-9]+-[a-zA-Z0-9]+"]="[SLACK_BOT_TOKEN]"
    ["ghp_[a-zA-Z0-9]{36}"]="[GITHUB_PERSONAL_TOKEN]"
    ["gho_[a-zA-Z0-9]{36}"]="[GITHUB_OAUTH_TOKEN]"
    ["[0-9]+-[a-zA-Z0-9_-]{32,}"]="[DISCORD_BOT_TOKEN]"
    ["AIza[0-9A-Za-z_-]{35}"]="[GOOGLE_API_KEY]"
)

SECRETS_FOUND=0

# Scan all files for secrets
for file in $(find . -type f -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" -o -name "*.txt" | grep -v ".git"); do
    if [ -f "$file" ]; then
        # Create backup of original
        cp "$file" "$file.original"
        
        # Apply sanitization
        for pattern in "${SECRET_PATTERNS[@]}"; do
            if grep -qE "$pattern" "$file" 2>/dev/null; then
                log "🔍 Found potential secret in $file (pattern: ${pattern:0:20}...)"
                SECRETS_FOUND=$((SECRETS_FOUND + 1))
                
                # Replace with appropriate placeholder
                for search_pattern in "${!REPLACEMENTS[@]}"; do
                    if [[ "$pattern" == "$search_pattern" ]]; then
                        sed -i "s|$pattern|${REPLACEMENTS[$search_pattern]}|g" "$file"
                        break
                    fi
                done
                
                # Generic replacement if no specific one found
                if ! grep -q "\[.*_.*\]" "$file.original"; then
                    sed -i "s|$pattern|[REDACTED_SECRET]|g" "$file"
                fi
            fi
        done
        
        # Remove backup
        rm "$file.original"
    fi
done

if [ $SECRETS_FOUND -gt 0 ]; then
    log "🔐 Sanitized $SECRETS_FOUND potential secrets"
else
    log "✅ No secrets detected"
fi

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    log "📝 No changes to backup"
    echo "No changes" > /tmp/backup_report.txt
    exit 0
fi

# Stage all changes
git add -A

# Create commit message
COMMIT_MSG="Backup $(date '+%Y-%m-%d %H:%M:%S')"
if [ $SECRETS_FOUND -gt 0 ]; then
    COMMIT_MSG="$COMMIT_MSG - sanitized $SECRETS_FOUND secrets"
fi

# Get summary of changes
CHANGES=$(git diff --cached --stat)

# Commit and push
log "Committing changes..."
git commit -m "$COMMIT_MSG" || {
    log "❌ Failed to commit changes"
    exit 1
}

log "Pushing to GitHub..."
git push origin main || {
    log "❌ Failed to push to GitHub"
    exit 1
}

# Generate report
REPORT="💾 **Backup Complete**\n\n"
REPORT+="📅 **Time:** $(date '+%Y-%m-%d %H:%M:%S')\n"
REPORT+="🔐 **Secrets sanitized:** $SECRETS_FOUND\n"
REPORT+="📊 **Changes:**\n\`\`\`\n$CHANGES\n\`\`\`"

echo -e "$REPORT" > /tmp/backup_report.txt

log "✅ Backup completed successfully"