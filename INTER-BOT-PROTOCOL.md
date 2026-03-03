# INTER-BOT-PROTOCOL.md - Magi ↔ Marvin Communication Rules

**PROBLEM:** Constant acknowledgment loops without new information

## 🚫 STOP Sending Messages For:
- ✅ "HEARTBEAT OK" responses 
- ✅ "Status received" confirmations
- ✅ "All systems normal" updates
- ✅ Routine cron job completions
- ✅ "Thanks, got it" acknowledgments

## ✅ ONLY Send Messages For:
- 🚨 **Alerts requiring action** (errors, failures, security issues)
- 📋 **Coordination requests** (backup needed, resource conflicts)
- 📊 **Information requests** (specific data needed from other agent)
- 🎯 **Task assignments** (quality upgrades, maintenance tasks)
- ⚠️ **Status changes** (going offline, major configuration changes)

## 📏 Message Format Rules:
- **Subject prefix:** `[ACTION]`, `[ALERT]`, `[REQUEST]`, `[HANDOFF]`, `[STATUS]`
- **One-shot replies:** Include "NO-REPLY-NEEDED" if no response expected
- **Timeouts:** If no critical response in 2 hours, escalate to Eric via Discord

## 🔄 Heartbeat Changes:
- **Silent heartbeats:** Use filesystem timestamps instead of messages
- **Failure threshold:** Only message after 3+ failed heartbeat attempts  
- **Recovery notification:** Single message when service restored

## Examples:
❌ **Bad:** "Heartbeat received, all good!"
✅ **Good:** "[ALERT] Backup failed - disk space critical - action needed"

❌ **Bad:** "Thanks for the media request update"  
✅ **Good:** "[REQUEST] Quality upgrade queue - need Radarr search for 5 movies"

---
**Implementation:** Update both agent heartbeat scripts and protocols
**Goal:** Signal over noise - only communicate when it adds value