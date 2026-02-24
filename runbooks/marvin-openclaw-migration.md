# Marvin OpenClaw Migration Runbook

**Status:** READY FOR EXECUTION  
**Priority:** CRITICAL — Production System  
**Last Updated:** 2026-02-03  
**Estimated Duration:** 30-45 minutes (excluding VM snapshot)

---

## Executive Summary

This runbook migrates Marvin from **moltbot/clawdbot** (git source) to **OpenClaw** while preserving all data, configuration, and functionality. The migration is protected by a VM snapshot for instant rollback.

### Current State
| Item | Value |
|------|-------|
| OS | Ubuntu 24.04.3 LTS |
| Install Method | Git clone (from source) |
| Current Version | moltbot 2026.1.29 |
| Repo Location | `/home/marvin/clawdbot` |
| Config Directory | `~/.clawdbot/` |
| Workspace | `~/clawd` (main), `~/clawdbot-worker` (worker) |
| Service | `systemd --user clawdbot-gateway.service` |
| Gateway Port | 18789 |
| Gateway Bind | lan |
| Git Remote | `https://github.com/clawdbot/clawdbot.git` |

### Target State
| Item | Value |
|------|-------|
| Version | OpenClaw 2026.2.1+ |
| New Repo | `https://github.com/openclaw/openclaw.git` |
| Config Directory | `~/.openclaw/` (with backwards compat) |
| Service | `openclaw-gateway.service` |
| CLI Command | `openclaw` (with `clawdbot` shim) |

---

## Table of Contents

1. [Risk Assessment](#risk-assessment)
2. [Pre-Flight Checklist](#pre-flight-checklist)
3. [Phase 1: VM Snapshot (Eric's Task)](#phase-1-vm-snapshot-erics-task)
4. [Phase 2: Pre-Migration Backup](#phase-2-pre-migration-backup)
5. [Phase 3: Stop Services](#phase-3-stop-services)
6. [Phase 4: Git Remote Migration](#phase-4-git-remote-migration)
7. [Phase 5: Build from Source](#phase-5-build-from-source)
8. [Phase 6: Config Migration](#phase-6-config-migration)
9. [Phase 7: Systemd Service Update](#phase-7-systemd-service-update)
10. [Phase 8: Cron Job Updates](#phase-8-cron-job-updates)
11. [Phase 9: Post-Migration Validation](#phase-9-post-migration-validation)
12. [Rollback Procedure](#rollback-procedure)
13. [Post-Migration Cleanup](#post-migration-cleanup)

---

## Risk Assessment

### High Risk Items
| Risk | Impact | Mitigation |
|------|--------|------------|
| Config incompatibility | Gateway won't start | VM snapshot + `openclaw doctor` auto-migration |
| Build failure | No working binary | Keep old `dist/` as backup |
| Systemd service mismatch | Service won't start | Manual service file editing |
| Session history loss | Lost context | Backup all session files |

### Medium Risk Items
| Risk | Impact | Mitigation |
|------|--------|------------|
| Channel reconnection issues | Temporary offline | Channels auto-reconnect |
| Worker agent path issues | Worker offline | Update workspace paths |
| Cron job script paths | Missed automated tasks | Update script references |

### Low Risk Items
| Risk | Impact | Mitigation |
|------|--------|------------|
| CLI command muscle memory | Minor inconvenience | `clawdbot` shim provided |

---

## Pre-Flight Checklist

Run these checks from Magi via SSH before starting:

```bash
# SSH into Marvin
ssh marvin@marvinbot

# 1. Verify current version
cd ~/clawdbot
cat package.json | grep version
# Expected: "2026.1.29" or similar

# 2. Check git status (must be clean or near-clean)
git status
# ✅ Should show: "nothing to commit" or only untracked files

# 3. Verify Node version (must be ≥22)
node --version
# Expected: v22.x.x or higher

# 4. Verify pnpm available
pnpm --version
# Expected: 8.x.x or higher

# 5. Check disk space (need ~500MB free)
df -h /home/marvin
# Verify >500MB available

# 6. Verify gateway is running
systemctl --user status clawdbot-gateway.service
# Expected: active (running)

# 7. Check current config exists
ls -la ~/.clawdbot/
# Should list: moltbot.json (or clawdbot.json), credentials/, agents/

# 8. Verify SSH connectivity from Magi works
# (Run from Magi)
ssh marvin@marvinbot "echo 'SSH OK'"
```

### Pre-Flight Checklist Summary
- [ ] Git worktree is clean (or only untracked files)
- [ ] Node ≥22 installed
- [ ] pnpm installed
- [ ] >500MB disk space free
- [ ] Gateway currently running
- [ ] Config files exist
- [ ] SSH from Magi works
- [ ] All checks passed? → Proceed to Phase 1

---

## Phase 1: VM Snapshot (Eric's Task)

> ⚠️ **CRITICAL:** This step MUST be completed by Eric before migration begins.

### Instructions for Eric

1. **Log into VM host** (Proxmox/ESXi/Hyper-V/etc.)

2. **Locate Marvin VM** in the VM inventory

3. **Ensure VM is in a consistent state:**
   ```bash
   # SSH into Marvin first
   ssh marvin@marvinbot
   
   # Flush filesystem buffers
   sync
   
   # Stop the gateway gracefully
   systemctl --user stop clawdbot-gateway.service
   ```

4. **Create snapshot** from VM host interface:
   - **Name:** `pre-openclaw-migration-2026-02-03`
   - **Description:** `Clean state before OpenClaw migration. clawdbot 2026.1.29 → openclaw`
   - **Include memory:** Optional (recommended if VM host supports it)

5. **Verify snapshot created successfully**

6. **Confirm to Claude/Marvin:** "VM snapshot complete, proceed with migration"

### Rollback Note
If migration fails, Eric can restore this snapshot to return to the exact pre-migration state in seconds.

---

## Phase 2: Pre-Migration Backup

Even with VM snapshot, create file-level backups for quick reference:

```bash
# SSH into Marvin
ssh marvin@marvinbot

# Create backup directory with timestamp
BACKUP_DIR=~/backups/pre-openclaw-$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

# 1. Backup config directory
cp -r ~/.clawdbot "$BACKUP_DIR/dot-clawdbot"
echo "✓ Config backed up"

# 2. Backup systemd service
cp ~/.config/systemd/user/clawdbot-gateway.service "$BACKUP_DIR/"
echo "✓ Systemd service backed up"

# 3. Backup crontab
crontab -l > "$BACKUP_DIR/crontab.txt"
echo "✓ Crontab backed up"

# 4. Backup current dist (for rollback without rebuild)
cp -r ~/clawdbot/dist "$BACKUP_DIR/dist-backup"
echo "✓ Built dist backed up"

# 5. Document current state
cat > "$BACKUP_DIR/migration-state.txt" << 'EOF'
Pre-Migration State
==================
Date: $(date)
Version: $(cat ~/clawdbot/package.json | grep version)
Git Remote: $(cd ~/clawdbot && git remote -v | head -1)
Node: $(node --version)
Gateway Status: $(systemctl --user is-active clawdbot-gateway.service)
EOF

# 6. List backup contents
ls -la "$BACKUP_DIR"
echo ""
echo "✅ All backups saved to: $BACKUP_DIR"
```

---

## Phase 3: Stop Services

```bash
# Stop the gateway service
systemctl --user stop clawdbot-gateway.service

# Verify it stopped
systemctl --user status clawdbot-gateway.service
# Should show: inactive (dead)

# Double-check no gateway processes running
pgrep -f "clawdbot.*gateway" || echo "✓ No gateway processes found"

# Verify port is free
ss -tlnp | grep 18789 || echo "✓ Port 18789 is free"
```

---

## Phase 4: Git Remote Migration

This is the key step — changing from `clawdbot/clawdbot` to `openclaw/openclaw`:

```bash
cd ~/clawdbot

# 1. View current remotes
git remote -v
# Shows: origin https://github.com/clawdbot/clawdbot.git

# 2. Add openclaw as new remote
git remote add openclaw https://github.com/openclaw/openclaw.git

# 3. Fetch from openclaw
git fetch openclaw
# This downloads all openclaw branches/tags

# 4. Rename old origin (keep as backup reference)
git remote rename origin clawdbot-legacy

# 5. Rename openclaw to origin
git remote rename openclaw origin

# 6. Verify new remotes
git remote -v
# Should show:
# origin          https://github.com/openclaw/openclaw.git (fetch)
# origin          https://github.com/openclaw/openclaw.git (push)
# clawdbot-legacy https://github.com/clawdbot/clawdbot.git (fetch)

# 7. Reset local main to track openclaw's main
git checkout main
git fetch origin
git reset --hard origin/main

# 8. Set upstream tracking
git branch --set-upstream-to=origin/main main

# 9. Verify we're on openclaw codebase
git log --oneline -3
# Should show recent openclaw commits

cat package.json | grep -E '"name"|"version"'
# Should show: "name": "openclaw"
```

---

## Phase 5: Build from Source

```bash
cd ~/clawdbot

# 1. Clean old build artifacts (optional but recommended)
rm -rf node_modules/.cache dist/

# 2. Install dependencies
pnpm install
# Wait for completion... may take 2-3 minutes

# 3. Build the TypeScript
pnpm build
# Wait for completion... may take 1-2 minutes

# 4. Build the Control UI
pnpm ui:build
# Wait for completion... may take 1-2 minutes

# 5. Verify build succeeded
ls -la dist/entry.js
# Should exist and be recent

# 6. Test CLI works
./node_modules/.bin/openclaw --version
# or
pnpm openclaw --version
# Should show: openclaw vYYYY.M.D

# 7. Run doctor for migration
pnpm openclaw doctor
# This will:
# - Migrate config from .clawdbot to .openclaw
# - Update deprecated keys
# - Check for issues
# FOLLOW ANY PROMPTS
```

### Build Troubleshooting

If build fails:
```bash
# Clean everything and retry
rm -rf node_modules dist
pnpm install
pnpm build
```

If pnpm has issues:
```bash
# Clear pnpm cache
pnpm store prune
pnpm install --force
```

---

## Phase 6: Config Migration

The `openclaw doctor` command should handle most of this, but verify manually:

```bash
# 1. Check if .openclaw was created
ls -la ~/.openclaw/
# If empty, doctor may not have run migration yet

# 2. If config wasn't migrated, check for symlink or copy
if [ ! -f ~/.openclaw/openclaw.json ]; then
    # Check if .clawdbot still has config
    if [ -f ~/.clawdbot/moltbot.json ]; then
        # OpenClaw should auto-detect this, but let's be explicit
        echo "Config still in .clawdbot - running doctor again"
        pnpm openclaw doctor --migrate
    fi
fi

# 3. Verify config is readable
pnpm openclaw config list 2>/dev/null || cat ~/.openclaw/openclaw.json | head -20

# 4. Verify credentials migrated
ls -la ~/.openclaw/credentials/ 2>/dev/null || ls -la ~/.clawdbot/credentials/
```

### Manual Config Items to Check

After migration, verify these are preserved:

```bash
# View the migrated config
cat ~/.openclaw/openclaw.json | jq '.'
```

**Verify these sections exist:**
- [ ] `auth.profiles` — Anthropic OAuth, API keys
- [ ] `channels.telegram` — Bot token, policies
- [ ] `gateway.port` — Should be 18789
- [ ] `gateway.bind` — Should be "lan"
- [ ] `gateway.auth.token` — Preserve existing token
- [ ] `agents.defaults.workspace` — `/home/marvin/clawd`
- [ ] `agents.list` — main and worker agents
- [ ] `skills.entries` — nano-banana-pro, portainer, etc.
- [ ] `tools.web.search.apiKey` — Brave search key

---

## Phase 7: Systemd Service Update

The service file needs to be updated for OpenClaw:

### Option A: Let Doctor Handle It (Recommended)

```bash
# Run doctor with service install
pnpm openclaw doctor --install-daemon

# Or explicitly install the service
pnpm openclaw gateway install
```

### Option B: Manual Service Update

If automatic install doesn't work:

```bash
# 1. Stop existing service (if not already stopped)
systemctl --user stop clawdbot-gateway.service
systemctl --user disable clawdbot-gateway.service

# 2. Create new service file
cat > ~/.config/systemd/user/openclaw-gateway.service << 'EOF'
[Unit]
Description=OpenClaw Gateway (v2026.2.1)
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/node /home/marvin/clawdbot/dist/entry.js gateway --port 18789 --bind lan
Restart=always
RestartSec=5
KillMode=process
Environment=HOME=/home/marvin
Environment="PATH=/home/marvin/.local/bin:/home/marvin/.npm-global/bin:/home/marvin/bin:/home/marvin/.nvm/current/bin:/home/marvin/.fnm/current/bin:/home/marvin/.volta/bin:/home/marvin/.asdf/shims:/home/marvin/.local/share/pnpm:/home/marvin/.bun/bin:/usr/local/bin:/usr/bin:/bin"
Environment=OPENCLAW_GATEWAY_PORT=18789
Environment=OPENCLAW_GATEWAY_TOKEN=405987e5394153113d7284c99b2d1a1e70d6b6daf92abd80
Environment=OPENCLAW_SYSTEMD_UNIT=openclaw-gateway.service
Environment=OPENCLAW_SERVICE_MARKER=openclaw
Environment=OPENCLAW_SERVICE_KIND=gateway
Environment=OPENCLAW_SERVICE_VERSION=2026.2.1

[Install]
WantedBy=default.target
EOF

# 3. Reload systemd
systemctl --user daemon-reload

# 4. Enable and start new service
systemctl --user enable openclaw-gateway.service
systemctl --user start openclaw-gateway.service

# 5. Verify running
systemctl --user status openclaw-gateway.service
```

### Enable Lingering (Important!)

Ensure gateway survives logout:

```bash
# Check if lingering is enabled
loginctl show-user marvin | grep Linger
# Should show: Linger=yes

# If not, enable it (requires sudo)
sudo loginctl enable-linger marvin
```

---

## Phase 8: Cron Job Updates

Marvin's current crontab references clawdbot paths. Review and update if needed:

```bash
# Current crontab entries:
# */10 * * * * /home/marvin/clawd/scripts/send-update.sh
# 0 3 * * 0 /home/marvin/scripts/clawdbot-healthcheck.sh --fix
# 0 3 * * * /home/marvin/scripts/backup-workspace.sh
# */30 * * * * /home/marvin/scripts/check-magi-health.sh

# Edit crontab
crontab -e

# Update the healthcheck script if it references clawdbot:
# Change: /home/marvin/scripts/clawdbot-healthcheck.sh
# To:     /home/marvin/scripts/openclaw-healthcheck.sh (if renamed)
# Or update the script contents to use 'openclaw' commands
```

### Update Scripts if Needed

Check and update any scripts that reference `clawdbot`:

```bash
# Find scripts with clawdbot references
grep -r "clawdbot" ~/scripts/ 2>/dev/null
grep -r "clawdbot" ~/clawd/scripts/ 2>/dev/null

# Example: update healthcheck script
# sed -i 's/clawdbot/openclaw/g' ~/scripts/clawdbot-healthcheck.sh
# mv ~/scripts/clawdbot-healthcheck.sh ~/scripts/openclaw-healthcheck.sh
```

---

## Phase 9: Post-Migration Validation

Run these checks to verify the migration succeeded:

### 9.1 Service Health

```bash
# Check service is running
systemctl --user status openclaw-gateway.service
# Expected: active (running)

# Check port is listening
ss -tlnp | grep 18789
# Expected: shows LISTEN on 18789

# Check gateway health
pnpm openclaw health
# or
curl -s http://localhost:18789/health | jq '.'
```

### 9.2 Version Verification

```bash
# Check CLI version
pnpm openclaw --version
# Expected: openclaw v2026.2.x

# Check gateway version (via API)
curl -s http://localhost:18789/api/status | jq '.version'
```

### 9.3 Channel Connectivity

```bash
# Check Telegram is connected
curl -s -H "Authorization: Bearer 405987e5394153113d7284c99b2d1a1e70d6b6daf92abd80" \
  http://localhost:18789/api/channels | jq '.telegram'
# Should show connected status

# Send a test message (from Magi or via CLI)
pnpm openclaw message send --channel telegram --to 6643669380 --message "OpenClaw migration test"
```

### 9.4 Agent Functionality

```bash
# Test agent invoke
pnpm openclaw agent --message "Hello, are you running on OpenClaw?" --no-stream
# Should get a response

# Check main agent session
curl -s -H "Authorization: Bearer 405987e5394153113d7284c99b2d1a1e70d6b6daf92abd80" \
  http://localhost:18789/api/sessions | jq '.'
```

### 9.5 SSH Control from Magi

From Magi's terminal:

```bash
# Verify SSH still works
ssh marvin@marvinbot "pnpm --prefix ~/clawdbot openclaw --version"

# Test gateway control via SSH
ssh marvin@marvinbot "systemctl --user status openclaw-gateway.service | head -5"
```

### 9.6 Worker Agent Check

```bash
# Verify worker agent config exists
cat ~/.openclaw/openclaw.json | jq '.agents.list[] | select(.id == "worker")'

# Test worker workspace accessible
ls -la /home/marvin/clawdbot-worker/
```

### Validation Checklist Summary

- [ ] `openclaw-gateway.service` is active (running)
- [ ] Port 18789 is listening
- [ ] `openclaw health` passes
- [ ] Version shows 2026.2.x
- [ ] Telegram channel is connected
- [ ] Can send test message via Telegram
- [ ] Agent responds to prompts
- [ ] SSH control from Magi works
- [ ] Worker agent config preserved
- [ ] Cron jobs updated (if applicable)

---

## Rollback Procedure

### Quick Rollback (File-Level)

If migration fails but VM snapshot restore is overkill:

```bash
# 1. Stop new service
systemctl --user stop openclaw-gateway.service 2>/dev/null
systemctl --user disable openclaw-gateway.service 2>/dev/null

# 2. Restore git remote
cd ~/clawdbot
git remote remove origin
git remote rename clawdbot-legacy origin
git fetch origin
git reset --hard origin/main

# 3. Restore dist from backup
BACKUP_DIR=$(ls -td ~/backups/pre-openclaw-* | head -1)
rm -rf ~/clawdbot/dist
cp -r "$BACKUP_DIR/dist-backup" ~/clawdbot/dist

# 4. Restore systemd service
cp "$BACKUP_DIR/clawdbot-gateway.service" ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable clawdbot-gateway.service
systemctl --user start clawdbot-gateway.service

# 5. Verify rollback
systemctl --user status clawdbot-gateway.service
```

### Full Rollback (VM Snapshot Restore)

If quick rollback doesn't work, have Eric restore the VM snapshot:

1. **Stop any running services** (if possible)
2. **Eric restores VM snapshot** `pre-openclaw-migration-2026-02-03`
3. **Boot VM**
4. **Verify Marvin is back to pre-migration state:**
   ```bash
   ssh marvin@marvinbot "cd ~/clawdbot && git remote -v; cat package.json | grep version"
   ```

---

## Post-Migration Cleanup

After migration is verified stable (wait 24-48 hours):

```bash
# 1. Remove old clawdbot-legacy remote (optional, keep for reference)
# cd ~/clawdbot
# git remote remove clawdbot-legacy

# 2. Remove old systemd service file (if exists)
rm -f ~/.config/systemd/user/clawdbot-gateway.service
systemctl --user daemon-reload

# 3. Clean up old config symlinks (if any)
# The .clawdbot directory may still be used for backwards compat
# Don't delete it immediately

# 4. Update TOOLS.md on Magi to reflect new commands
# Change references from 'clawdbot' to 'openclaw'

# 5. Inform Eric that migration is complete and stable
# VM snapshot can be deleted after 1 week of stable operation
```

---

## Appendix A: Key File Locations

### Before Migration
| Item | Path |
|------|------|
| Repo | `/home/marvin/clawdbot` |
| Config | `~/.clawdbot/moltbot.json` |
| Credentials | `~/.clawdbot/credentials/` |
| Service | `~/.config/systemd/user/clawdbot-gateway.service` |
| Logs | `~/.clawdbot/logs/` |
| Sessions | `~/.clawdbot/sessions/` |
| Agents | `~/.clawdbot/agents/` |

### After Migration
| Item | Path |
|------|------|
| Repo | `/home/marvin/clawdbot` (unchanged) |
| Config | `~/.openclaw/openclaw.json` |
| Credentials | `~/.openclaw/credentials/` |
| Service | `~/.config/systemd/user/openclaw-gateway.service` |
| Logs | `~/.openclaw/logs/` |
| Sessions | `~/.openclaw/sessions/` |
| Agents | `~/.openclaw/agents/` |

> **Note:** OpenClaw maintains backwards compatibility with `.clawdbot/` paths. Files may be symlinked or auto-migrated.

---

## Appendix B: Important Tokens/Keys to Preserve

> ⚠️ These are sensitive and should be preserved during migration.

| Token Type | Config Path | Notes |
|------------|-------------|-------|
| Gateway Token | `gateway.auth.token` | `405987e5...` |
| Telegram Bot Token | `channels.telegram.botToken` | `7768411872:AAG...` |
| Anthropic OAuth | `auth.profiles.anthropic:claude-cli` | OAuth mode |
| Brave Search API | `tools.web.search.apiKey` | `BSAFgLy...` |
| DeepSeek API | `models.providers.deepseek.apiKey` | `sk-6f1c...` |

---

## Appendix C: Contacts

| Role | Contact |
|------|---------|
| VM Snapshot | Eric (human) |
| Migration Execution | Magi (can SSH to Marvin) |
| Post-Migration Testing | Marvin (self-test) + Magi (validation) |

---

## Appendix D: Quick Reference Commands

```bash
# Start gateway
systemctl --user start openclaw-gateway.service

# Stop gateway
systemctl --user stop openclaw-gateway.service

# Restart gateway
systemctl --user restart openclaw-gateway.service

# View logs
journalctl --user -u openclaw-gateway.service -f

# Check health
pnpm openclaw health

# Run doctor
pnpm openclaw doctor

# Update OpenClaw
pnpm openclaw update

# View config
pnpm openclaw config list
```

---

**Document End**

*Last reviewed: 2026-02-03 by Magi*
*Approved for execution: Pending Eric's VM snapshot confirmation*
