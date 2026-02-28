#!/bin/bash
# Daily Briefing Cron Job - Posts to Discord at 8 AM EST

# Source environment
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
cd /home/magi/clawd

# Generate briefing
BRIEFING=$(bash scripts/daily-briefing.sh 2>/dev/null)

# Discord channel ID for #general
CHANNEL_ID="1475371906008875133"
GUILD_ID="1475371904578621470"

# Post to Discord using OpenClaw message tool
python3 << PYTHON_EOF
import subprocess
import json

briefing = """$BRIEFING"""

# Use OpenClaw message command
result = subprocess.run([
    'openclaw', 'message', 'send',
    '--channel', 'discord',
    '--target', f'channel:{CHANNEL_ID}',
    '--message', briefing
], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ Daily briefing posted to Discord #general")
else:
    print(f"❌ Failed to post: {result.stderr}")
    exit(1)
PYTHON_EOF
