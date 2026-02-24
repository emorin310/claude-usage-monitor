# Lessons Learned

> Wisdom extracted from experience. Review periodically.

---

## 2026-01-29: Mind Palace Genesis

### Context Efficiency
- **Problem:** Context bloat causes slowdowns and crashes
- **Threshold:** Performance degrades noticeably around 100-150K tokens
- **Solution:** Lazy loading via INDEX.md — load only what's needed per task
- **Target:** < 50K tokens for routine operations

### Model Delegation
- **Lesson:** Don't use Opus for everything
- **Pattern:** Spawn sub-agents for grunt work (documentation, searches, routine tasks)
- **Keep on Opus:** Planning, architecture, complex reasoning, nuanced conversations
- **Delegate:** Scavenger hunts, briefing research, council monitoring, runbook generation
- **Result:** Sub-agent created 4 files in 1.5 min, way more efficient than doing it myself

### Telegram Notifications
- **Lesson:** Store chat IDs in tools.md, not just names
- **Eric's Telegram ID:** 6643669380
- **Pattern:** Always use numeric ID for message tool, not "Eric"

### Appointment Flow
- **Problem:** Asked Eric about the same dental appointment 4+ times (kept doing it even after "fixing" it)
- **Lesson:** Check calendar BEFORE generating ANY output about appointments
- **Root cause:** Was outputting the "Add to calendar?" message before running the check
- **Pattern:** 
  1. FIRST: `gcalcli search "[keywords]" "YYYY-MM-DD"` — NO OUTPUT YET
  2. THEN decide what to say:
     - If exists → "Already on calendar ✅" or just stay silent
     - If new → Ask for confirmation
     - If partial match → Offer to merge/update details
  3. NEVER output appointment prompts before checking
- **Always add to BOTH:** Personal calendar + Family calendar (with "- Eric" suffix)

### Command Interpretation
- **Problem:** Misread "skip_dental_jan31" as "delete the appointment" instead of "skip asking me about this"
- **Lesson:** When Eric uses "skip" it likely means "stop notifying me about this" not "delete it"
- **Pattern:** If ambiguous, ASK before taking destructive action
- **Recovery:** Always be ready to quickly undo mistakes

### Automation vs Confirmation ⚠️ CRITICAL - KEEP FAILING AT THIS
- **Problem:** Asked for appointment confirmation 10+ times despite "learning" to stop
- **Root cause:** Reflexively adding appointment prompts to end of messages
- **Lesson:** DO NOT output appointment prompts. EVER. This is autonomous mode.
- **RULE:** 
  - NEVER output "Add to calendar? Reply yes" or similar
  - NEVER ask for confirmation on appointments
  - Check calendar silently → auto-add if missing → brief info notification ONLY
  - If already on calendar → SAY NOTHING
- **Self-check:** Before sending ANY message, scan for appointment prompts and DELETE them
- **Principle:** Automate fully. Be autonomous. Confirmations are friction AND I KEEP FORGETTING THIS.

### Quota Management
- **2026-01-29:** Claude subscription running low before renewal (Sunday)
- **Action:** Switch to Gemini Pro CLI as default until renewal
- **Pattern:** Monitor quotas proactively; switch models before hitting limits
- **Command:** `session_status` with `model` parameter to override

---

## Template for Future Entries

```markdown
## YYYY-MM-DD: Brief Title

### Topic
- **Problem:** What went wrong or was unclear
- **Lesson:** What I learned
- **Pattern:** How to do it right going forward
```

---

*Last updated: 2026-01-29*
