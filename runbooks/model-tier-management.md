# Model Tier Management & Auto-Switching Runbook

**Version:** 1.0  
**Last Updated:** 2026-02-01  
**Owner:** Magi (tested), Marvin (pending implementation)  
**Purpose:** Optimize AI model usage for cost efficiency while maintaining quality

---

## Quick Decision Tree

```
New Task Arrives
    │
    ├─ Is it human conversation? ────────────────────► Keep current model
    │
    ├─ Usage >75%? ─────────────────────────────────► Use Gemini or sub-agent
    │
    ├─ Complex reasoning/architecture? ──────────────► Opus (if usage <75%)
    │
    ├─ Multi-step grunt work? ───────────────────────► Spawn sub-agent
    │
    └─ Routine task? ────────────────────────────────► Sonnet or Gemini
```

---

## Part 1: Check Current Usage

**Before making model decisions, know where you stand:**

```bash
# Quick check
/status

# Or via session_status tool
session_status()
```

**Interpret the output:**
- **0-50%**: Green zone - use Opus freely
- **50-75%**: Yellow zone - be selective with Opus
- **75-90%**: Orange zone - Sonnet/Gemini only, sub-agents for heavy work
- **90%+**: Red zone - Gemini only, alert Eric

---

## Part 2: Model Selection by Task Type

### High-Value Tasks (Opus)
✅ **Use when:**
- System architecture or design decisions
- Complex debugging requiring deep reasoning
- Writing documentation/RFCs/runbooks
- Nuanced human conversations (main session)
- Multi-step planning with dependencies
- Security-sensitive decisions

❌ **Don't use for:**
- Simple lookups or status checks
- Routine file operations
- Formatting/parsing
- Bulk operations

**How to switch:**
```bash
# Via session_status (preferred)
session_status(model="opus")

# Verify
/status
```

---

### Balanced Tasks (Sonnet)
✅ **Use when:**
- General code generation/review
- Standard task execution
- Opus usage >75%
- Most day-to-day work
- Moderate complexity tasks

**How to switch:**
```bash
session_status(model="sonnet")
```

---

### Routine Tasks (Gemini)
✅ **Use when:**
- Heartbeat checks
- Simple queries
- Background monitoring
- Quick lookups
- File organization

**Models available:**
- `google/gemini-2.0-flash-exp` (recommended - fast + capable)
- `google/gemini-1.5-pro` (balanced)
- `google/gemini-1.5-flash` (lightweight)

**How to switch:**
```bash
session_status(model="google/gemini-2.0-flash-exp")
```

---

## Part 3: Sub-Agent Delegation

**Spawn sub-agents for parallelizable or heavy work that doesn't need your main session context.**

### When to Delegate
✅ **Spawn sub-agent for:**
- Documentation generation
- Web research compilation
- Bulk operations (copying tasks, formatting data)
- Runbook creation
- Long-running analysis
- Any work that can be summarized back

❌ **Keep on main agent:**
- Direct human conversation
- Decisions requiring session context
- Security-sensitive operations
- Tasks needing immediate interaction

### How to Spawn

```javascript
// Basic spawn
sessions_spawn({
  task: "Research and compile top 5 homelab monitoring tools with pros/cons",
  label: "research-monitoring-tools",  // Optional: easier to track
  cleanup: "delete"  // Auto-delete when done
})

// With model override (for heavy work)
sessions_spawn({
  task: "Generate comprehensive runbook for Syncthing backup setup",
  model: "sonnet",  // Use cheaper model for sub-agent
  cleanup: "keep"   // Keep session for review
})

// Check on sub-agents
sessions_list({
  kinds: ["spawn"],
  limit: 10
})
```

**Sub-agent will:**
1. Do the work in isolation
2. Ping main session when complete
3. Deliver summary/results

---

## Part 4: Failsafe Auto-Switch System

**Automatic fallback when quota is exceeded - prevents complete downtime.**

### How It Works

```
Every 15 minutes (system cron)
    │
    ├─ Health check agent
    ├─ Detect quota/rate limit errors
    ├─ Auto-switch to free model (Gemini)
    └─ Notify Eric via Telegram
```

### Setup (One-Time)

**Step 1: Create failsafe script**

```bash
# Create directories
mkdir -p ~/clawd-marvin/scripts
mkdir -p ~/clawd-marvin/logs

# Create script
nano ~/clawd-marvin/scripts/failsafe-model-switch.sh
```

**Script content:**

```bash
#!/bin/bash
# Agent Failsafe: Auto-switch to free model if quota exceeded

# CUSTOMIZE THESE:
AGENT_NAME="marvin"              # Your agent name
SESSION="main"                    # Session key (usually "main")
FREE_MODEL="google/gemini-2.0-flash-exp"  # Free fallback
TELEGRAM_CHAT_ID="6643669380"    # Eric's Telegram

LOG_FILE="$HOME/clawd-$AGENT_NAME/logs/failsafe.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Test if agent can respond
RESPONSE=$(clawdbot session send --session "$SESSION" --message "HEALTH_CHECK" --timeout 10 2>&1)

if [[ $? -ne 0 ]] || [[ "$RESPONSE" =~ "quota" ]] || [[ "$RESPONSE" =~ "rate limit" ]] || [[ "$RESPONSE" =~ "exceeded" ]]; then
    echo "[$TIMESTAMP] ⚠️ $AGENT_NAME unresponsive or quota error. Switching to $FREE_MODEL..." >> "$LOG_FILE"
    
    # Switch to free model
    clawdbot session model --session "$SESSION" --model "$FREE_MODEL" >> "$LOG_FILE" 2>&1
    
    # Notify Eric
    clawdbot message send --channel telegram --target "$TELEGRAM_CHAT_ID" \
        --message "🚨 **Failsafe Triggered: $AGENT_NAME**

Hit quota limits and auto-switched to $FREE_MODEL (free tier).

Reduced capabilities but still operational! 🖥️" >> "$LOG_FILE" 2>&1
    
    echo "[$TIMESTAMP] ✅ Switched to $FREE_MODEL and notified Eric" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] ✓ $AGENT_NAME healthy" >> "$LOG_FILE"
fi
```

**Step 2: Make executable**

```bash
chmod +x ~/clawd-marvin/scripts/failsafe-model-switch.sh
```

**Step 3: Test manually**

```bash
~/clawd-marvin/scripts/failsafe-model-switch.sh
tail ~/clawd-marvin/logs/failsafe.log
```

**Step 4: Add to system cron**

```bash
crontab -e

# Add this line (runs every 15 minutes):
*/15 * * * * $HOME/clawd-marvin/scripts/failsafe-model-switch.sh
```

**Step 5: Verify cron**

```bash
crontab -l  # Should show your new entry
```

---

## Part 5: Real-World Scenarios

### Scenario 1: Morning Briefing (Routine)
**Task:** Generate daily briefing with calendar, weather, tasks

**Decision:**
- Routine task = Gemini
- Already running as recurring task
- No need for expensive model

**Action:** None (already on Gemini via recurring task)

---

### Scenario 2: Architecture Planning (Complex)
**Task:** Design multi-agent coordination system

**Decision:**
- Complex reasoning = Opus
- Check usage first
- If usage >75%, spawn sub-agent instead

**Action:**
```bash
# Check usage
/status

# If <75%:
session_status(model="opus")

# If >75%:
sessions_spawn({
  task: "Design multi-agent coordination system with communication protocols",
  model: "opus",
  cleanup: "keep"
})
```

---

### Scenario 3: Bulk Data Processing (Grunt Work)
**Task:** Copy 100 Todoist tasks from one project to another

**Decision:**
- Parallelizable = Sub-agent
- Doesn't need main session context
- Can use cheaper model

**Action:**
```javascript
sessions_spawn({
  task: "Copy all tasks from 'Old Project' to 'New Project' in Todoist, preserving labels and due dates",
  model: "sonnet",
  cleanup: "delete"
})
```

---

### Scenario 4: Usage at 80% (Emergency Mode)
**Situation:** Opus quota at 80%, important work incoming

**Decision:**
- Switch main session to Gemini
- Use sub-agents for everything non-conversational
- Reserve remaining Opus for critical decisions only

**Actions:**
```bash
# Switch main to Gemini
session_status(model="google/gemini-2.0-flash-exp")

# Notify Eric
message({
  action: "send",
  channel: "telegram",
  target: "6643669380",
  message: "⚠️ **Model Usage Alert**\n\nOpus quota: 80%\n\nSwitched to Gemini for routine tasks. Will use sub-agents for heavy work. 🖥️"
})
```

---

## Part 6: Recovery & Monitoring

### Check Failsafe Logs

```bash
# Recent activity
tail -20 ~/clawd-marvin/logs/failsafe.log

# Count triggers today
grep "$(date '+%Y-%m-%d')" ~/clawd-marvin/logs/failsafe.log | grep "Failsafe Triggered"
```

### Manual Model Reset

When quotas reset (daily/monthly), switch back:

```bash
# Return to default
session_status(model="default")

# Or specify
session_status(model="opus")
```

### Check Sub-Agent Status

```bash
# List recent sub-agents
sessions_list({
  kinds: ["spawn"],
  limit: 10,
  messageLimit: 3  # Include last 3 messages
})

# Check specific sub-agent
sessions_history({
  sessionKey: "spawn-label-here",
  limit: 20
})
```

---

## Part 7: Best Practices

### DO ✅
- Check usage before switching to Opus
- Use sub-agents for parallelizable work
- Set up failsafe system (runs independently)
- Log model switches in memory files
- Notify Eric at 75% and 90% thresholds
- Test failsafe script before adding to cron

### DON'T ❌
- Use Opus for simple lookups
- Spawn sub-agents for human conversation
- Switch models mid-conversation without reason
- Ignore usage warnings
- Rely solely on manual switching (failsafe is insurance)

---

## Part 8: Troubleshooting

### "Session model command not working"
**Fix:** Use `session_status(model="...")` instead of manual commands

### "Sub-agent not responding"
**Check:**
```bash
sessions_list({kinds: ["spawn"]})
# Look for status, check if completed
```

### "Failsafe not triggering"
**Debug:**
```bash
# Check cron is running
crontab -l

# Check logs
tail -f ~/clawd-marvin/logs/failsafe.log

# Test manually
~/clawd-marvin/scripts/failsafe-model-switch.sh
```

### "High usage but still using Opus"
**Immediate action:**
```bash
session_status(model="google/gemini-2.0-flash-exp")
```

---

## Quick Reference Card

| Usage | Main Session | New Tasks | Heavy Work |
|-------|--------------|-----------|------------|
| 0-50% | Opus | Opus OK | Opus or sub-agent |
| 50-75% | Opus/Sonnet | Selective Opus | Sub-agent (Sonnet) |
| 75-90% | Gemini | Sonnet/Gemini | Sub-agent (Sonnet) |
| 90%+ | Gemini | Gemini only | Sub-agent (Gemini) |

**Commands to memorize:**
```bash
/status                          # Check usage
session_status(model="...")      # Switch model
sessions_spawn({task: "..."})    # Delegate work
```

---

## Related KB Articles
- 🤖 AI Model Selection Guide (Task ID: 9966359969)
- 🛡️ Model Quota Failsafe System (Task ID: 9972166451)

---

**End of Runbook**

*Last tested: Magi 2026-02-01*  
*Status: Production-ready for Marvin*
