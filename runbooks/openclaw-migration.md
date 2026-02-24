# OpenClaw Migration Runbook

**Migration:** clawdbot 2026.1.24-3 → OpenClaw 2026.2.1+  
**Agent:** Magi  
**Host:** Magrathea (Mac Studio)  
**Date Created:** 2026-02-03  
**Author:** Magi (subagent)  
**Status:** Ready for Review

---

## Executive Summary

This runbook documents the migration from **clawdbot 2026.1.24-3** (npm package) to **OpenClaw** (the open-source rebrand). OpenClaw is the same project with:
- Renamed npm package (`clawdbot` → `openclaw`)
- Renamed config directory (`~/.clawdbot` → `~/.openclaw`)
- Updated launchd service labels (`com.clawdbot.*` → `bot.molt.*`)
- Built-in auto-migration for legacy paths

**Risk Level:** LOW (with proper backups)  
**Expected Downtime:** 5-15 minutes  
**Rollback Window:** Immediate (within first 24 hours)

---

## Table of Contents

1. [Pre-Migration Assessment](#1-pre-migration-assessment)
2. [Backup Procedures](#2-backup-procedures)
3. [Migration Steps](#3-migration-steps)
4. [Configuration Changes](#4-configuration-changes)
5. [Post-Migration Validation](#5-post-migration-validation)
6. [Rollback Procedure](#6-rollback-procedure)
7. [Risk Assessment](#7-risk-assessment)
8. [Troubleshooting](#8-troubleshooting)
9. [Reference Information](#9-reference-information)

---

## 1. Pre-Migration Assessment

### 1.1 Current Environment

| Component | Current Value | Notes |
|-----------|--------------|-------|
| **Package** | clawdbot@2026.1.24-3 | npm global install |
| **CLI Path** | /opt/homebrew/bin/clawdbot | Homebrew node |
| **Config** | ~/.clawdbot/clawdbot.json | Primary config |
| **Workspace** | /Users/eric/clawd-magi | Agent workspace |
| **Gateway Port** | 18789 | Default port |
| **Gateway Bind** | lan | LAN access enabled |
| **launchd Service** | com.clawdbot.gateway | Currently running (PID tracked) |
| **Node Version** | v25.2.1 | Exceeds minimum (≥22) ✓ |

### 1.2 Pre-Flight Checklist

Run these checks BEFORE starting migration:

```bash
# 1. Verify current version
clawdbot --version
# Expected: 2026.1.24-3

# 2. Check gateway status
clawdbot gateway status
# Should show: running

# 3. Verify node version
node --version
# Should be ≥ v22.0.0

# 4. Check disk space (need ~500MB free)
df -h ~
# Verify adequate space

# 5. List active cron jobs
clawdbot cron list
# Document all jobs (see section 9.3)

# 6. Test Telegram connectivity
# Send a test message to verify bot is responsive

# 7. Check for running subagents/sessions
clawdbot session list 2>/dev/null || echo "No active sessions"
```

### 1.3 Inventory of Critical Data

**Identity Files (WORKSPACE: /Users/eric/clawd-magi):**
- [x] SOUL.md - Core identity
- [x] AGENTS.md - Workspace behavior
- [x] USER.md - User context
- [x] MEMORY.md - Long-term memory
- [x] TOOLS.md - Local notes
- [x] IDENTITY.md - Identity metadata
- [x] COUNCIL.md - Council operations manual
- [x] HEARTBEAT.md - Heartbeat instructions

**Memory System:**
- [x] memory/*.md - Daily notes (24+ files)
- [x] memory/council-state.json - Council communication state
- [x] memory/journal.md - Journal entries
- [x] memory/contacts.md - Contact information
- [x] journal.md - Root journal

**Configuration (~/.clawdbot/):**
- [x] clawdbot.json - Main config
- [x] credentials/ - OAuth tokens, Gmail auth
- [x] devices/paired.json - Paired nodes
- [x] telegram/ - Telegram state
- [x] cron/*.json - All cron jobs
- [x] exec-approvals.json - Approved commands
- [x] .env - Environment variables

**Scripts & Automation:**
- [x] scripts/*.sh - Custom scripts (25 files)
- [x] venv/ - Python virtual environment

---

## 2. Backup Procedures

### 2.1 Full Backup Script

Create and run this backup script:

```bash
#!/bin/bash
# openclaw-migration-backup.sh
# Run this BEFORE migration

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/openclaw-migration-backup-${BACKUP_DATE}"

echo "🦞 OpenClaw Migration Backup"
echo "============================"
echo "Backup location: ${BACKUP_DIR}"
echo ""

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# 1. Backup entire clawdbot config directory
echo "📁 Backing up ~/.clawdbot..."
cp -R ~/.clawdbot "${BACKUP_DIR}/clawdbot-config"

# 2. Backup workspace
echo "📁 Backing up workspace..."
cp -R /Users/eric/clawd-magi "${BACKUP_DIR}/clawd-magi-workspace"

# 3. Backup launchd plist (if exists)
echo "📁 Backing up launchd service..."
if [ -f ~/Library/LaunchAgents/com.clawdbot.gateway.plist ]; then
    cp ~/Library/LaunchAgents/com.clawdbot.gateway.plist "${BACKUP_DIR}/"
fi

# 4. Export npm global list
echo "📦 Documenting npm globals..."
npm list -g --depth=0 > "${BACKUP_DIR}/npm-globals.txt"

# 5. Capture current cron jobs
echo "⏰ Capturing cron configuration..."
clawdbot cron list > "${BACKUP_DIR}/cron-jobs.txt" 2>&1

# 6. Capture gateway status
echo "🔍 Capturing gateway status..."
clawdbot gateway status > "${BACKUP_DIR}/gateway-status.txt" 2>&1

# 7. Create checksums for verification
echo "🔐 Creating checksums..."
find "${BACKUP_DIR}" -type f -exec shasum -a 256 {} \; > "${BACKUP_DIR}/checksums.sha256"

# 8. Create manifest
echo "📋 Creating backup manifest..."
cat > "${BACKUP_DIR}/MANIFEST.md" << EOF
# Migration Backup Manifest
**Created:** $(date)
**Source Version:** clawdbot 2026.1.24-3
**Target Version:** OpenClaw latest

## Contents
- clawdbot-config/ - Full ~/.clawdbot directory
- clawd-magi-workspace/ - Full workspace
- com.clawdbot.gateway.plist - launchd service (if present)
- npm-globals.txt - npm global packages
- cron-jobs.txt - Cron job listing
- gateway-status.txt - Gateway status at backup time
- checksums.sha256 - File integrity verification

## Restoration
See openclaw-migration.md section 6 for restoration procedure.
EOF

echo ""
echo "✅ Backup complete!"
echo "📁 Location: ${BACKUP_DIR}"
echo ""
echo "Verify backup size:"
du -sh "${BACKUP_DIR}"
```

**Save this script and run:**
```bash
# Create the script
cat > ~/openclaw-migration-backup.sh << 'SCRIPT'
# [paste script content above]
SCRIPT

# Make executable and run
chmod +x ~/openclaw-migration-backup.sh
~/openclaw-migration-backup.sh
```

### 2.2 Verify Backup Integrity

```bash
# Navigate to backup directory
cd ~/openclaw-migration-backup-*/

# Verify key files exist
ls -la clawdbot-config/clawdbot.json
ls -la clawdbot-config/credentials/
ls -la clawd-magi-workspace/SOUL.md
ls -la clawd-magi-workspace/memory/

# Verify checksums
shasum -a 256 -c checksums.sha256 | grep -c "OK"
# Should match total file count
```

### 2.3 Git Commit Workspace

```bash
cd /Users/eric/clawd-magi
git status
git add -A
git commit -m "Pre-OpenClaw migration snapshot - $(date +%Y-%m-%d)"
git push origin main 2>/dev/null || echo "No remote configured"
```

---

## 3. Migration Steps

### 3.1 Stop the Gateway

```bash
# Method 1: CLI (preferred)
clawdbot gateway stop

# Method 2: launchctl (if CLI fails)
launchctl bootout gui/$UID/com.clawdbot.gateway

# Verify stopped
clawdbot gateway status
# Should show: not running

# Double-check no lingering processes
pgrep -f clawdbot
# Should return nothing
```

### 3.2 Install OpenClaw

```bash
# Install OpenClaw globally (keeps clawdbot as shim)
npm install -g openclaw@latest

# Verify installation
openclaw --version
# Should show: 2026.2.1 (or newer)

# Verify clawdbot shim still works
clawdbot --version
# Should show same version
```

### 3.3 Run Migration Doctor

The `openclaw doctor` command handles automatic migration:

```bash
# Run doctor - this will:
# - Migrate ~/.clawdbot → ~/.openclaw (or keep both with symlinks)
# - Update config keys (cacheControlTtl → cacheRetention)
# - Update launchd service (com.clawdbot → bot.molt)
# - Audit security settings

openclaw doctor
```

**Expected doctor actions:**
1. **Config migration:** Auto-migrates `~/.clawdbot/clawdbot.json` → `~/.openclaw/openclaw.json`
2. **Legacy shim:** Creates compatibility symlinks/pointers
3. **Service update:** Rewrites launchd plist from `com.clawdbot.gateway` → `bot.molt.gateway`
4. **Security audit:** Warns on any risky DM policies

### 3.4 Install/Update Gateway Service

```bash
# Install the new launchd service
openclaw gateway install

# Or run onboard to ensure everything is configured
openclaw onboard --no-wizard
```

### 3.5 Start the Gateway

```bash
# Start via CLI
openclaw gateway start

# Or restart if already running
openclaw gateway restart

# Verify running
openclaw gateway status
# Should show: running

# Check launchctl
launchctl list | grep -E "(claw|molt)"
# Should show bot.molt.gateway
```

### 3.6 Verify Channels

```bash
# Check Telegram
openclaw channels status

# Send test message
openclaw message send --target 6643669380 --message "🦞 OpenClaw migration test - please confirm receipt"
```

---

## 4. Configuration Changes

### 4.1 Breaking Changes in OpenClaw

| Change | Old (clawdbot) | New (OpenClaw) | Auto-Migrated? |
|--------|----------------|----------------|----------------|
| Config path | ~/.clawdbot/ | ~/.openclaw/ | ✓ Yes |
| Config file | clawdbot.json | openclaw.json | ✓ Yes |
| CLI binary | clawdbot | openclaw | ✓ (shim exists) |
| launchd label | com.clawdbot.gateway | bot.molt.gateway | ✓ Yes |
| Session logs | .clawdbot paths | .openclaw paths | ✓ Yes |
| Gateway auth | mode:"none" allowed | mode:"none" REMOVED | ⚠️ Must fix |

### 4.2 Config Key Renames

These are automatically migrated by `openclaw doctor`:

```json
// Old key → New key
"cacheControlTtl" → "cacheRetention"
```

### 4.3 Security Changes (IMPORTANT)

**Gateway auth mode "none" is REMOVED in OpenClaw.**

Your current config has:
```json
"gateway": {
  "auth": {
    "mode": "token",
    "token": "ec788e78c55feb2f970e14a41ea10a2d656155e650ae3f25"
  }
}
```

**✓ You're already compliant** - no changes needed.

If you had `mode: "none"`, you would need to:
```bash
# Generate a new token
openclaw gateway token generate

# Or set a password
openclaw config set gateway.auth.mode password
openclaw config set gateway.auth.password "your-secure-password"
```

### 4.4 Environment Variables

New environment variables for multi-instance setups:
```bash
# Old
CLAWDBOT_CONFIG_PATH=~/.clawdbot/custom.json

# New (both work, new preferred)
OPENCLAW_CONFIG_PATH=~/.openclaw/custom.json
OPENCLAW_STATE_DIR=~/.openclaw-state
```

### 4.5 Scripts/Scripts that Reference "clawdbot"

Check your scripts for hardcoded "clawdbot" commands:

```bash
# Find references in your workspace
grep -r "clawdbot" ~/clawd-magi/scripts/
```

**The `clawdbot` shim remains available**, so existing scripts should continue to work. However, consider updating them to use `openclaw` for future-proofing.

---

## 5. Post-Migration Validation

### 5.1 Immediate Validation Checklist

Run these checks immediately after migration:

```bash
#!/bin/bash
# post-migration-check.sh

echo "🦞 OpenClaw Post-Migration Validation"
echo "====================================="

# 1. Version check
echo -n "1. Version: "
openclaw --version

# 2. Gateway status
echo -n "2. Gateway: "
openclaw gateway status | head -1

# 3. Config location
echo -n "3. Config: "
ls ~/.openclaw/openclaw.json 2>/dev/null && echo "✓ ~/.openclaw/openclaw.json" || echo "⚠️ Using legacy path"

# 4. launchd service
echo -n "4. launchd: "
launchctl list | grep -q "bot.molt.gateway" && echo "✓ bot.molt.gateway running" || echo "⚠️ Service not found"

# 5. Cron jobs
echo "5. Cron jobs:"
openclaw cron list | head -5

# 6. Channel status
echo "6. Channels:"
openclaw channels status 2>/dev/null || echo "   (check manually)"

# 7. Memory files accessible
echo -n "7. Memory: "
ls /Users/eric/clawd-magi/memory/*.md 2>/dev/null | wc -l | xargs echo "files found"

# 8. Identity files
echo -n "8. Identity: "
for f in SOUL.md AGENTS.md MEMORY.md; do
    [ -f "/Users/eric/clawd-magi/$f" ] && echo -n "✓$f " || echo -n "✗$f "
done
echo ""
```

### 5.2 Functional Tests

```bash
# Test 1: Send Telegram message
openclaw message send --target 6643669380 --message "Post-migration test 1: Direct message ✓"

# Test 2: Agent turn
openclaw agent --message "Say 'Post-migration test successful' - one line only"

# Test 3: Cron job check
openclaw cron list | grep -c "enabled.*true"
# Should match your expected enabled job count (11)

# Test 4: Web search (if enabled)
openclaw agent --message "Search for 'OpenClaw latest release' - just confirm search works"

# Test 5: Read workspace file
openclaw agent --message "Read SOUL.md and confirm you can see my identity"
```

### 5.3 Validate Cron Jobs

Verify all cron jobs are intact:

```bash
# List all jobs
openclaw cron list

# Expected jobs (11):
# - usage-monitor (*/30 * * * *)
# - marvin-health-monitor (*/30 * * * *)
# - gmail-monitor (0 */2 * * *)
# - log-rotation (0 0 * * *)
# - session-model-monitor (0 */3 * * *)
# - session-health-check (0 3 * * *)
# - morning-briefing (0 8 * * *)
# - todoist-monitor (0 9,12,15,18 * * *)
# - council-monitor (0 10,18 * * *)
# - afternoon-research (0 14 * * *)
# - weekly-digest (0 9 * * 0)

# Wait for next cron job to fire and verify it works
```

### 5.4 Validate Integrations

**Telegram (@magrathea_as_bot):**
- [ ] Bot responds to messages
- [ ] Reactions work
- [ ] Media sending works

**Todoist Council:**
- [ ] API calls work (check council-state.json updates)
- [ ] Comments can be posted

**Marvin Communication:**
- [ ] SSH to marvin@marvinbot works
- [ ] Health monitor can reach Marvin

### 5.5 24-Hour Monitoring

After migration, monitor for:
- [ ] Morning briefing fires correctly (8am)
- [ ] Todoist monitor runs (9am, 12pm, 3pm, 6pm)
- [ ] Council monitor updates (10am, 6pm)
- [ ] No unexpected gateway restarts
- [ ] Heartbeat system works (every 30m)

---

## 6. Rollback Procedure

### 6.1 Quick Rollback (Within 24 Hours)

If something goes wrong, rollback immediately:

```bash
# 1. Stop OpenClaw gateway
openclaw gateway stop

# 2. Uninstall OpenClaw
npm uninstall -g openclaw

# 3. Install original clawdbot version
npm install -g clawdbot@2026.1.24-3

# 4. Restore config backup
BACKUP_DIR=$(ls -td ~/openclaw-migration-backup-* | head -1)
cp -R "${BACKUP_DIR}/clawdbot-config/"* ~/.clawdbot/

# 5. Restore launchd service
cp "${BACKUP_DIR}/com.clawdbot.gateway.plist" ~/Library/LaunchAgents/ 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.clawdbot.gateway.plist

# 6. Start gateway
clawdbot gateway start

# 7. Verify
clawdbot --version
clawdbot gateway status
```

### 6.2 Full Rollback (Data Restoration)

If workspace data was corrupted:

```bash
# 1. Stop everything
openclaw gateway stop 2>/dev/null
clawdbot gateway stop 2>/dev/null

# 2. Restore full workspace from backup
BACKUP_DIR=$(ls -td ~/openclaw-migration-backup-* | head -1)
rm -rf /Users/eric/clawd-magi
cp -R "${BACKUP_DIR}/clawd-magi-workspace" /Users/eric/clawd-magi

# 3. Restore config
rm -rf ~/.clawdbot ~/.openclaw
cp -R "${BACKUP_DIR}/clawdbot-config" ~/.clawdbot

# 4. Reinstall original version
npm install -g clawdbot@2026.1.24-3

# 5. Restore and start service
cp "${BACKUP_DIR}/com.clawdbot.gateway.plist" ~/Library/LaunchAgents/
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.clawdbot.gateway.plist
clawdbot gateway start

# 6. Verify git state
cd /Users/eric/clawd-magi
git status
git log -1
```

### 6.3 Partial Rollback (Config Only)

If only config is problematic:

```bash
# Stop gateway
openclaw gateway stop

# Restore just config
BACKUP_DIR=$(ls -td ~/openclaw-migration-backup-* | head -1)
cp "${BACKUP_DIR}/clawdbot-config/clawdbot.json" ~/.openclaw/openclaw.json

# Restart
openclaw gateway start
```

---

## 7. Risk Assessment

### 7.1 Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Config migration fails | Low | Medium | Backup + manual migration |
| Cron jobs lost | Very Low | High | Jobs stored in ~/.clawdbot/cron/, backed up |
| Telegram bot disconnects | Low | Medium | Bot token unchanged; reconnect automatic |
| OAuth tokens invalidated | Very Low | Low | Tokens preserved in credentials/ |
| Memory files lost | Very Low | Critical | Git + backup + workspace untouched |
| Gateway won't start | Low | High | Rollback available; logs for debugging |
| launchd service conflict | Low | Medium | Old service stopped before new installed |

### 7.2 Mitigations Already In Place

1. **Automatic migration:** OpenClaw's doctor handles config migration
2. **Compatibility shim:** `clawdbot` command still works
3. **Workspace untouched:** Migration only affects ~/.clawdbot, not workspace
4. **Full backup:** Pre-migration backup captures everything
5. **Git versioning:** Workspace is git-tracked

### 7.3 Critical Success Factors

- ✓ Backup completed and verified
- ✓ Gateway stopped cleanly
- ✓ Doctor migration runs without errors
- ✓ New gateway starts successfully
- ✓ Telegram bot responds
- ✓ Cron jobs fire on schedule

---

## 8. Troubleshooting

### 8.1 Gateway Won't Start

```bash
# Check logs
openclaw logs --follow

# Check if port is in use
lsof -i :18789

# Try manual start with verbose
openclaw gateway --port 18789 --verbose

# Check launchd logs
log show --predicate 'subsystem == "bot.molt"' --last 5m
```

### 8.2 Config Not Found

```bash
# Check both locations
ls -la ~/.clawdbot/clawdbot.json
ls -la ~/.openclaw/openclaw.json

# Force config path
OPENCLAW_CONFIG_PATH=~/.clawdbot/clawdbot.json openclaw gateway status

# Manually create symlink if needed
ln -s ~/.clawdbot/clawdbot.json ~/.openclaw/openclaw.json
```

### 8.3 Telegram Not Responding

```bash
# Check channel status
openclaw channels status

# Verify bot token in config
grep -A2 "telegram" ~/.openclaw/openclaw.json

# Test with direct API call
curl "https://api.telegram.org/bot8556347438:AAFc2TSO2ELdHqhNywgCS2gO5Xmc_-O8rF4/getMe"
```

### 8.4 Cron Jobs Missing

```bash
# Check cron directory
ls -la ~/.openclaw/cron/ 2>/dev/null || ls -la ~/.clawdbot/cron/

# Recreate if needed (example for morning-briefing)
openclaw cron create --name morning-briefing --cron "0 8 * * *" --tz "America/Toronto" --message "☀️ Morning briefing..."
```

### 8.5 launchd Service Issues

```bash
# Remove old service
launchctl bootout gui/$UID/com.clawdbot.gateway 2>/dev/null

# Check new service exists
ls ~/Library/LaunchAgents/bot.molt.gateway.plist

# Load manually
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/bot.molt.gateway.plist

# Check status
launchctl print gui/$UID/bot.molt.gateway
```

---

## 9. Reference Information

### 9.1 File Locations

| Item | Old Location | New Location |
|------|--------------|--------------|
| Config | ~/.clawdbot/clawdbot.json | ~/.openclaw/openclaw.json |
| Credentials | ~/.clawdbot/credentials/ | ~/.openclaw/credentials/ |
| Cron | ~/.clawdbot/cron/ | ~/.openclaw/cron/ |
| Devices | ~/.clawdbot/devices/ | ~/.openclaw/devices/ |
| Telegram | ~/.clawdbot/telegram/ | ~/.openclaw/telegram/ |
| launchd | ~/Library/LaunchAgents/com.clawdbot.gateway.plist | ~/Library/LaunchAgents/bot.molt.gateway.plist |

### 9.2 API Keys & Tokens (DO NOT EXPOSE)

All preserved in config migration:
- Telegram Bot Token: `channels.telegram.botToken`
- Groq API Key: `models.providers.groq.apiKey`
- DeepSeek API Key: `models.providers.deepseek.apiKey`
- Google API Key: `models.providers.google.apiKey`
- Moonshot API Key: `models.providers.moonshot.apiKey`
- Brave Search Key: `tools.web.search.apiKey`
- Gateway Token: `gateway.auth.token`
- Todoist Token: In TOOLS.md (workspace file)

### 9.3 Current Cron Job Inventory

| Job ID | Name | Schedule | Agent | Model |
|--------|------|----------|-------|-------|
| f2ab... | usage-monitor | */30 * * * * | worker | deepseek-reasoner |
| d23f... | marvin-health-monitor | */30 * * * * | worker | deepseek-reasoner |
| 7d9c... | gmail-monitor | 0 */2 * * * | worker | deepseek-reasoner |
| e953... | log-rotation | 0 0 * * * | worker | deepseek-reasoner |
| 0e9b... | session-model-monitor | 0 */3 * * * | worker | deepseek-reasoner |
| 5cd1... | session-health-check | 0 3 * * * | worker | deepseek-reasoner |
| 8dfa... | morning-briefing | 0 8 * * * | worker | deepseek-reasoner |
| 1460... | todoist-monitor | 0 9,12,15,18 * * * | worker | deepseek-reasoner |
| 160c... | council-monitor | 0 10,18 * * * | worker | deepseek-reasoner |
| de5b... | afternoon-research | 0 14 * * * | worker | deepseek-reasoner |
| 1f1f... | weekly-digest | 0 9 * * 0 | worker | deepseek-reasoner |

### 9.4 Useful Commands Reference

```bash
# Version check
openclaw --version

# Gateway management
openclaw gateway status
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
openclaw logs --follow

# Channels
openclaw channels status
openclaw channels login  # Re-pair WhatsApp if needed

# Cron
openclaw cron list
openclaw cron enable <id>
openclaw cron disable <id>

# Config
openclaw config get gateway.port
openclaw config set gateway.port 18789

# Health check
openclaw doctor
openclaw health

# Update
openclaw update --channel stable
```

### 9.5 Documentation Links

- **OpenClaw Docs:** https://docs.openclaw.ai/
- **Updating Guide:** https://docs.openclaw.ai/install/updating
- **Troubleshooting:** https://docs.openclaw.ai/gateway/troubleshooting
- **Security:** https://docs.openclaw.ai/gateway/security
- **GitHub Releases:** https://github.com/openclaw/openclaw/releases
- **Discord Support:** https://discord.gg/clawd

---

## Appendix A: Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                  OPENCLAW MIGRATION QUICK REF               │
├─────────────────────────────────────────────────────────────┤
│ BEFORE:                                                     │
│   ./openclaw-migration-backup.sh                            │
│   clawdbot gateway stop                                     │
│                                                             │
│ MIGRATE:                                                    │
│   npm install -g openclaw@latest                            │
│   openclaw doctor                                           │
│   openclaw gateway install                                  │
│   openclaw gateway start                                    │
│                                                             │
│ VERIFY:                                                     │
│   openclaw --version                                        │
│   openclaw gateway status                                   │
│   openclaw cron list                                        │
│   launchctl list | grep molt                                │
│                                                             │
│ ROLLBACK:                                                   │
│   openclaw gateway stop                                     │
│   npm uninstall -g openclaw                                 │
│   npm install -g clawdbot@2026.1.24-3                       │
│   cp -R ~/openclaw-migration-backup-*/clawdbot-config/*     │
│        ~/.clawdbot/                                         │
│   clawdbot gateway start                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Appendix B: Post-Migration Maintenance

After successful migration:

1. **Clean up backup** (after 7 days of stable operation):
   ```bash
   rm -rf ~/openclaw-migration-backup-*
   ```

2. **Update documentation** in workspace if you reference "clawdbot":
   ```bash
   grep -r "clawdbot" ~/clawd-magi/*.md
   # Update references to "openclaw" where appropriate
   ```

3. **Update scripts** to use `openclaw` command (optional, shim works):
   ```bash
   # Check scripts
   grep -l "clawdbot" ~/clawd-magi/scripts/*.sh
   ```

4. **Consider updating TOOLS.md** with any new OpenClaw-specific notes.

---

**Migration runbook complete. 🦞**

*This document was generated by Magi for Eric's clawdbot → OpenClaw migration.*
