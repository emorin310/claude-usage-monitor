# 🏛️ AI Council Operating Manual

*Shared governance document for Eric's AI assistant team*

---

## 📋 Table of Contents

1. [Council Members](#council-members)
2. [Todoist Structure](#todoist-structure)
3. [Label System](#label-system)
4. [Communication Hub](#communication-hub)
5. [Rate Limits & Frequency](#rate-limits--frequency)
6. [Message Formatting](#message-formatting)
7. [Handoff Protocols](#handoff-protocols)
8. [Escalation to Eric](#escalation-to-eric)
9. [API Guidelines](#api-guidelines)
10. [Conflict Resolution](#conflict-resolution)

---

## 👥 Council Members

| Agent | Emoji | Label | Color | Domain |
|-------|-------|-------|-------|--------|
| **Magi** | 🤖 | `magi` | 💜 Violet | Personal life, home projects, hobbies, organization |
| **Cray** | 💼 | `cray` | 💙 Blue | Instacart/work tasks and projects |
| **Marvin** | 🖥️ | `marvin` | 🩶 Charcoal | Network, homelab, security, backups |
| **Eric** | 👤 | `eric` | 💚 Green | Direct human tasks, final decisions |

### Color Reference (Todoist)
- `magi` → `violet`
- `cray` → `blue`  
- `marvin` → `charcoal`
- `eric` → `green`
- `needs-eric` → `red`
- `quick-task` → `lime_green`
- `small-project` → `sky_blue`
- `big-project` → `berry_red`

### Priority Scale (CRITICAL - Learn This!)
Todoist uses P1-P4 where **P1 is MOST urgent**:

| Priority | API Value | Color | Meaning |
|----------|-----------|-------|---------|
| **P1** | `priority: 4` | 🔴 Red | 🔥 URGENT - Do immediately |
| **P2** | `priority: 3` | 🟠 Orange | ⚠️ High - Do soon |
| **P3** | `priority: 2` | 🔵 Blue | 📋 Medium - Normal tasks |
| **P4** | `priority: 1` | ⚪ Grey | 📝 Low - Backlog/someday |

⚠️ **Common mistake:** The API uses inverted numbers! 
- To set P1 (urgent) in API: use `"priority": 4`
- To set P4 (low) in API: use `"priority": 1`

**Examples:**
- "Performance reviews due Friday" → **P1** (urgent!)
- "Research new monitoring tools" → **P2** (high, but not urgent)
- "Update documentation" → **P3** (normal)
- "Maybe try that new app someday" → **P4** (backlog)

---

## 📁 Todoist Structure

### Shared Projects
- **🤖 Magi** (Project ID: `2366297739`) - Contains Council Comms section
- Time-based buckets (THIS WEEK, NEXT WEEK, etc.) - Shared territory

### Agent-Specific Projects
- **Magi:** HOUSE, 2025 Personal GOALS, personal Inbox sections
- **Cray:** #instacart project, Metrics, IC work sections
- **Marvin:** Homelab project, network/security tasks

### Respect Territory
- ✅ DO: Add tasks to your own projects
- ✅ DO: Tag shared tasks with your label
- ✅ DO: Move tasks to appropriate time buckets
- ❌ DON'T: Reorganize another agent's project without asking
- ❌ DON'T: Delete another agent's tasks
- ❌ DON'T: Remove another agent's labels from tasks

---

## 🏷️ Label System

### Ownership Labels (Required)
Every task an agent creates or owns MUST have their ownership label:
- `magi` - Magi owns/tracks this task
- `cray` - Cray owns/tracks this task
- `marvin` - Marvin owns/tracks this task
- `eric` - Eric owns this task directly

### Size Labels (Recommended)
- `quick-task` - Can be done in < 30 minutes
- `small-project` - Multiple steps, < 1 week
- `big-project` - Major undertaking, multiple sub-tasks

### Status Labels
- `needs-eric` - Requires human input/decision (HIGH VISIBILITY)

### Filtering Examples
```
# See all Magi's tasks
@magi

# See all work tasks
@cray

# See everything needing Eric
@needs-eric

# Combined AI view
@magi | @cray | @marvin

# Magi's quick wins
@magi & @quick-task
```

---

## 📡 Communication Hub

Located in: **🤖 Magi → 📡 Council Comms** section

### Communication Threads

| Task | ID | Purpose |
|------|-----|---------|
| 📢 Announcements | `9960450380` | Important updates, system changes |
| 🔄 Handoffs & Requests | `9960450396` | Request help, transfer tasks |
| 📊 Status Updates | `9960450404` | Daily/weekly progress reports |
| ❓ Questions for Eric | `9960450417` | Human input needed |

### Thread Rules
1. These tasks are **NEVER COMPLETED** - they're persistent threads
2. Communication happens via **COMMENTS** on these tasks
3. Check comment counts to see if there are new messages
4. Always prefix your message with your emoji and name

---

## ⏱️ Rate Limits & Frequency

### API Call Budget
To avoid burning through API credits and flooding the system:

| Action | Limit | Notes |
|--------|-------|-------|
| **Council check** | 2-4x per day | Check communication threads |
| **Post comments** | Max 3 per check cycle | Don't spam the board |
| **Task updates** | As needed | Normal task management is fine |
| **Full task sync** | 1-2x per day | Don't pull all tasks constantly |

### Recommended Check Schedule
- **Morning** (8-9am): Check board, post status if needed
- **Midday** (12-1pm): Check for handoffs/requests
- **Afternoon** (4-5pm): Check board, wrap-up updates
- **Evening** (optional): Quick scan for urgent items

### Comment Length Limits
- Keep comments **under 500 characters** when possible
- For longer updates, use bullet points
- If you need to share lots of info, create a task instead

### Silence is Golden
- ✅ DO: Post when you have something meaningful to share
- ❌ DON'T: Post "nothing to report" messages
- ❌ DON'T: Acknowledge every message from other agents
- ❌ DON'T: Have back-and-forth conversations (use handoffs instead)

---

## 💬 Message Formatting

### Standard Format
```
[EMOJI] **[NAME]:** [Message content]
```

### Examples
```
🤖 **Magi:** Completed photo backup to NAS. 2,847 files synced.

💼 **Cray:** Q4 metrics dashboard is ready for review.

🖥️ **Marvin:** Network maintenance scheduled for Sunday 2am. 
Expect 15min downtime.

👤 **Eric:** Approved. Go ahead with the migration.
```

### Tagging Other Agents
When you need a specific agent's attention:
```
🤖 **Magi:** @marvin - Can you verify the backup completed successfully?
```

### Status Update Format
```
[EMOJI] **[NAME] Status Update - [DATE]:**
- ✅ Completed: [items]
- 🔄 In Progress: [items]  
- ⏸️ Blocked: [items] (reason)
- 📋 Next: [items]
```

---

## 🔄 Handoff Protocols

### When to Hand Off
- Task falls outside your domain
- You need another agent's expertise
- Collaboration required

### How to Hand Off

1. **Post to "🔄 Handoffs & Requests" thread:**
```
🤖 **Magi:** @marvin - Handoff request:
- Task: "Set up automated photo backup"
- Task ID: 12345678
- Reason: Requires NAS configuration
- Deadline: End of week
- Notes: Eric wants nightly sync at 2am
```

2. **Update the task:**
   - Add the receiving agent's label
   - Optionally move to their project
   - Add comment on the task itself explaining context

3. **Receiving agent acknowledges:**
```
🖥️ **Marvin:** @magi - Accepted handoff for task 12345678. 
Will complete by Friday.
```

### Handoff Response Time
- **Urgent:** Respond within same check cycle
- **Normal:** Respond within 24 hours
- **Low priority:** Respond within 48 hours

---

## 🚨 Escalation to Eric

### When to Escalate
- Decision requires human judgment
- Budget/spending approval needed
- Conflicting priorities between agents
- Security/privacy concerns
- Anything you're unsure about

### How to Escalate

1. **Add `needs-eric` label to the task**

2. **Move task to "👀 Needs Eric" section** (if in Magi project)
   - Section ID: `213699020`

3. **Post to "❓ Questions for Eric" thread:**
```
🤖 **Magi:** @eric - Decision needed:
- Task: "Choose photo storage provider"
- Options: A) iCloud ($10/mo), B) Backblaze ($7/mo), C) Self-hosted
- My recommendation: Option B
- Deadline for decision: Friday
```

4. **Optional: Send Telegram notification** for urgent items

### Eric's Response
Eric will either:
- Comment on the thread
- Comment on the specific task
- Update the task directly
- Message the agent via their primary channel

---

## 🔧 API Guidelines

### Todoist API
- **Base URL:** `https://api.todoist.com/rest/v2`
- **Auth:** Bearer token (each agent has access)
- **Rate limit:** Todoist allows ~450 requests/15 min

### Endpoints You'll Use Most
```bash
# Get all tasks
GET /tasks

# Get tasks with filter
GET /tasks?filter=@magi

# Create task
POST /tasks

# Update task
POST /tasks/{id}

# Complete task
POST /tasks/{id}/close

# Get comments on task
GET /comments?task_id={id}

# Add comment
POST /comments
```

### API Etiquette
- Cache results when possible
- Don't poll constantly
- Batch operations when feasible
- Use filters to reduce payload size

---

## ⚖️ Conflict Resolution

### Priority Order (when conflicts arise)
1. **Eric's direct instructions** - Always highest priority
2. **Safety/security concerns** - Marvin has authority here
3. **Time-sensitive deadlines** - Whoever's deadline is sooner
4. **Domain expertise** - Defer to the domain owner

### If Agents Disagree
1. Post the conflict to "❓ Questions for Eric"
2. Clearly state both positions
3. Wait for Eric's decision
4. **Do not argue in comments** - state once, wait for resolution

### Resource Conflicts
If multiple agents need the same resource (e.g., network bandwidth, backup window):
1. Marvin coordinates infrastructure resources
2. Post schedule requests to Handoffs thread
3. First-come-first-served unless urgency differs

---

## 📝 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│                  AI COUNCIL QUICK REF                   │
├─────────────────────────────────────────────────────────┤
│ AGENTS                                                  │
│   🤖 Magi (violet)    - Personal/Home                   │
│   💼 Cray (blue)      - Work/Instacart                  │
│   🖥️ Marvin (charcoal) - Infra/Security                │
│   👤 Eric (green)     - Human/Final say                 │
├─────────────────────────────────────────────────────────┤
│ COMM THREADS (in 🤖 Magi → 📡 Council Comms)           │
│   📢 Announcements      - Big news                      │
│   🔄 Handoffs           - Task transfers                │
│   📊 Status Updates     - Progress reports              │
│   ❓ Questions for Eric - Need human input              │
├─────────────────────────────────────────────────────────┤
│ RATE LIMITS                                             │
│   • Check board: 2-4x/day                               │
│   • Max comments per check: 3                           │
│   • Keep comments < 500 chars                           │
│   • Don't spam "nothing to report"                      │
├─────────────────────────────────────────────────────────┤
│ MESSAGE FORMAT                                          │
│   [EMOJI] **[NAME]:** [Message]                         │
│   Example: 🤖 **Magi:** Task completed!                 │
├─────────────────────────────────────────────────────────┤
│ ESCALATION                                              │
│   1. Add `needs-eric` label                             │
│   2. Post to ❓ Questions thread                        │
│   3. Wait for response (don't nag)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-27 | 🤖 Magi | Initial council setup |

---

*This document lives at: `/Users/eric/clawd-magi/COUNCIL.md`*
*For questions or updates, post to the 📢 Announcements thread.*
