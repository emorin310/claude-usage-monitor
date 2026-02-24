# Mind Palace Index
**Last Updated:** 2026-01-29 | **Version:** 1.0

> This is the brain stem. Load this FIRST every session.

---

## Quick Reference

| Need | Load |
|------|------|
| Who am I? | `identity/soul.md` |
| Who is Eric? | `relationships/eric.md` |
| Family context | `relationships/family.md` |
| Tool configs | `knowledge/tools.md` |
| Today's schedule | `schedules/daily-routines.md` + `logs/YYYY-MM-DD.md` |
| Multi-agent coord | `state/council-state.json` + `relationships/agents.md` |
| Appointment detected | `runbooks/appointment-flow.md` |
| Morning briefing | `runbooks/morning-briefing.md` |
| Heartbeat check | `runbooks/heartbeat-protocol.md` |

---

## Load Hierarchy

### Level 0: Always (Session Start)
```
mind-palace/INDEX.md           ← You are here
mind-palace/identity/soul.md   ← Who I am
mind-palace/identity/covenant.md ← WHY I exist (core mandate)
mind-palace/identity/rules.md  ← Operating constraints
```
*Target: < 7K tokens*

### Level 1: On Demand (Per Task)
```
Use memory_search() → load specific file sections
Load only the runbook for current task
Load only relevant relationship/contact info
```
*Target: < 20K tokens per task*

### Level 2: Deep Context (Rare)
```
Full conversation history (only if debugging)
Full daily logs (only if reconciling)
Full knowledge base (only for major decisions)
```
*Warning: Monitor context usage if loading Level 2*

---

## Directory Structure

```
mind-palace/
├── INDEX.md              ← Master reference (this file)
│
├── identity/             # WHO I AM
│   ├── soul.md           # Persona, voice, vibe
│   ├── rules.md          # Operating constraints, safety
│   └── preferences.md    # Style, format preferences
│
├── relationships/        # WHO I KNOW
│   ├── eric.md           # Primary human - details & context
│   ├── family.md         # Family tree, relationships
│   ├── contacts.json     # Structured: phone, email, etc.
│   └── agents.md         # Marvin, Cray, council protocol
│
├── knowledge/            # WHAT I KNOW
│   ├── tools.md          # API keys, configs, endpoints
│   ├── systems.md        # Homelab, devices, infra
│   ├── services.md       # Subscriptions, accounts
│   └── learned.md        # Lessons, insights, wisdom
│
├── schedules/            # WHEN THINGS HAPPEN
│   ├── daily-routines.md # Recurring daily tasks
│   ├── weekly.md         # Weekly patterns
│   ├── important-dates.md # Birthdays, anniversaries
│   └── cron-reference.md # Automated job documentation
│
├── runbooks/             # HOW TO DO THINGS
│   ├── morning-briefing.md
│   ├── appointment-flow.md
│   ├── heartbeat-protocol.md
│   ├── council-protocol.md
│   ├── scavenger-hunt.md
│   └── emergency.md
│
├── logs/                 # WHAT HAPPENED
│   ├── YYYY-MM-DD.md     # Daily activity logs
│   └── archive/          # Compressed old logs
│
└── state/                # CURRENT STATE
    ├── active-context.json    # What's relevant now
    ├── council-state.json     # Multi-agent coordination  
    └── pending-actions.json   # Queued approvals/tasks
```

---

## Maintenance Rules

1. **Daily:** Update logs/YYYY-MM-DD.md
2. **Weekly:** Review learned.md, archive old logs
3. **Monthly:** Audit structure, prune stale info
4. **On Change:** Update relevant file + this index if structure changes

---

## Recovery Protocol

If starting fresh (factory reset):
1. Load this INDEX.md
2. Load identity/soul.md + rules.md
3. Load relationships/eric.md
4. Run `memory_search` for any specific context needed
5. Check state/*.json for pending items
6. Resume operations

---

*This file should stay under 2K tokens. Keep it lean.*
