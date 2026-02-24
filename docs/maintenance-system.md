# Automated Maintenance & Health System

🎯 **Goal:** Keep Magi running smoothly with minimal manual intervention while providing intelligent monitoring.

## 📦 What We Just Built

### 1. Auto-Update System (4:00 AM daily)
- **Updates OpenClaw package** to latest version
- **Updates gateway** components  
- **Restarts services** after updates
- **Reports results** to Discord #monitoring
- **Logs everything** to `/home/magi/clawd/logs/auto-update.log`

### 2. GitHub Backup System (4:30 AM daily)  
- **Backs up all critical files** (SOUL.md, MEMORY.md, scripts, skills, etc.)
- **Scans for secrets** and replaces with safe placeholders
- **Commits and pushes** to private GitHub repository
- **Reports status** to Discord #monitoring
- **Enables disaster recovery** - can restore entire setup from repo

### 3. Comprehensive Health Monitoring (Every 30 min, 7 AM - 11 PM)
- **Gmail monitoring** - Flags urgent emails (payment failures, security alerts, meeting changes)
- **Calendar alerts** - Warns about events in next 2 hours
- **System health** - Monitors disk space, memory usage, service status
- **Todoist tracking** - Council communications, overdue tasks
- **Smart alerting** - Only notifies when action needed (no "all clear" spam)

### 4. Enhanced Heartbeat System
- **Coordinates with cron jobs** - avoids duplication
- **Handles complex reasoning** that cron can't do
- **Reviews automated alerts** and escalates if needed
- **Maintains memory files** and workspace organization

## 🚀 How to Enable

### Step 1: Set up GitHub backup (optional but recommended)
Follow the guide: `/home/magi/clawd/docs/setup-github-backup.md`

### Step 2: Install cron jobs
```bash
/home/magi/clawd/scripts/setup-maintenance-crons.sh
```

### Step 3: Verify installation  
```bash
crontab -l | grep -A 10 "OpenClaw Maintenance"
```

### Step 4: Test manually (optional)
```bash
# Test update script
/home/magi/clawd/scripts/auto-update.sh

# Test backup script  
/home/magi/clawd/scripts/github-backup.sh

# Test health checks
/home/magi/clawd/scripts/comprehensive-health-check.sh
```

## 📊 Monitoring

### Discord Notifications
All status updates go to your Discord #monitoring channel:
- ✅ Successful updates/backups
- ❌ Failures with error details  
- 🚨 Health alerts requiring attention

### Log Files
- **Updates:** `/home/magi/clawd/logs/auto-update.log`
- **Backups:** `/home/magi/clawd/logs/backup.log`  
- **Health:** `/home/magi/clawd/logs/comprehensive-health.log`

### State Tracking
- **Council state:** `memory/council-state.json`
- **Health state:** `memory/health-state.json`

## ⚙️ Configuration

### Timing (can be customized in crontab)
- **4:00 AM** - Auto-updates
- **4:30 AM** - GitHub backup
- **Every 30 min (7 AM - 11 PM)** - Health checks

### Alerting Rules
**Urgent** (immediate attention):
- Payment failures, security alerts
- Events starting in <1 hour
- System critical (disk >95%, services down)

**Heads Up** (action today):  
- Upcoming meetings (next 2 hours)
- Subscription renewals
- Overdue tasks

**No Alert:**
- Routine status updates
- Normal system metrics
- Already-handled issues

## 🛠️ Customization

### Add Custom Health Checks
Edit `/home/magi/clawd/scripts/comprehensive-health-check.sh` and add new check types.

### Modify Notification Targets
Update cron jobs to send to different Discord channels or add Telegram/WhatsApp notifications.

### Adjust Timing
```bash
crontab -e
# Modify the schedule lines
```

### Add New Backup Items
Edit `/home/magi/clawd/scripts/github-backup.sh` to include additional files or directories.

## 🔒 Security Features

- **Secret scanning** - Automatically detects and redacts API keys, tokens, passwords
- **Draft-only email** - Never sends emails automatically, only creates drafts
- **Approval gates** - Destructive actions require confirmation
- **Audit trails** - Everything logged with timestamps
- **Private backups** - GitHub repo should be private

## 🚨 Troubleshooting

### Cron Jobs Not Running
```bash
# Check if cron service is running
sudo systemctl status cron

# Check cron logs
sudo tail -f /var/log/syslog | grep CRON
```

### Permission Issues
```bash
# Make scripts executable
chmod +x /home/magi/clawd/scripts/*.sh

# Check file ownership
ls -la /home/magi/clawd/scripts/
```

### Discord Notifications Not Working
```bash
# Test message sending
echo "Test message" | openclaw message send --channel discord --target monitoring
```

### GitHub Backup Failing
```bash
# Test SSH connection
ssh -T git@github.com

# Check if repo exists and is accessible
git clone YOUR_REPO_URL /tmp/test_clone
```

## 📈 Next Steps

This system provides the foundation for:
- **Service monitoring** (when you add Coolify or similar)
- **Email automation** (beyond draft-only mode)
- **Calendar management** (family scheduling)
- **Home Assistant integration** (smart home monitoring)

The infrastructure is ready - just add the specific integrations you need!

---

*This system implements workflows #3 and #4 from the velvet-shark gist, adapted for your specific setup and security requirements.*