# GitHub Backup Setup Guide

## Step 1: Create Private Repository

1. Go to GitHub and create a new **private** repository named `magi-backup`
2. Initialize with a README (optional)
3. Copy the repository URL

## Step 2: Set Up SSH Key (if not already done)

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub
```

Then add the public key to GitHub:
- Go to GitHub Settings → SSH and GPG keys
- Click "New SSH key"
- Paste the public key

## Step 3: Update Backup Script

Edit `/home/magi/clawd/scripts/github-backup.sh` and update:

```bash
REPO_URL="git@github.com:YOUR_USERNAME/magi-backup.git"
```

Replace `YOUR_USERNAME` with your GitHub username.

## Step 4: Test the Setup

```bash
# Test SSH connection
ssh -T git@github.com

# Run backup script manually to test
/home/magi/clawd/scripts/github-backup.sh
```

## Step 5: What Gets Backed Up

The script backs up:
- **Core files:** SOUL.md, MEMORY.md, USER.md, IDENTITY.md, TOOLS.md, AGENTS.md, HEARTBEAT.md
- **Memory directory:** All daily logs and memory files
- **Scripts:** All automation scripts
- **Skills:** Custom skill configurations  
- **Cron jobs:** Current crontab configuration
- **OpenClaw config:** Gateway configuration

## Step 6: Security Features

The backup script automatically:
- **Scans for secrets** (API keys, tokens, passwords)
- **Replaces with placeholders** like `[OPENAI_API_KEY]`, `[DISCORD_BOT_TOKEN]`
- **Logs what was sanitized** in commit messages
- **Preserves functionality** while removing sensitive data

## Monitoring

- **Success:** Gets reported to Discord #monitoring channel
- **Failure:** Check `/home/magi/clawd/logs/backup.log`
- **Manual run:** `/home/magi/clawd/scripts/github-backup.sh`

## Repository Structure

After first backup, your repo will look like:
```
magi-backup/
├── SOUL.md
├── MEMORY.md  
├── USER.md
├── IDENTITY.md
├── TOOLS.md
├── AGENTS.md
├── HEARTBEAT.md
├── memory/
│   ├── 2026-02-24.md
│   ├── council-state.json
│   └── ...
├── scripts/
│   ├── auto-update.sh
│   ├── github-backup.sh
│   └── ...
├── skills/
│   └── [any custom skills]
├── crontab.txt
└── openclaw-config.yaml
```

## Recovery

To restore from backup:
1. Clone the repository
2. Review sanitized files and replace placeholders with actual secrets
3. Copy files back to `/home/magi/clawd/`
4. Restore crontab: `crontab crontab.txt`
5. Restore OpenClaw config to `~/.openclaw/config.yaml`