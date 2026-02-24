# Gmail Triage & Automation System

**Goal:** Keep Gmail tidy, rarely need to check it, only see important new stuff.

**Owner:** Magi (with Council support)  
**Status:** 🔄 In Progress  
**Created:** 2026-02-03

---

## Philosophy

Eric should:
- ✅ Rarely need to look at Gmail
- ✅ Only see NEW important stuff when checking
- ✅ Get notified via Telegram for critical items
- ✅ Get Todoist tasks for "needs review" items
- ✅ Know old items are safely archived with labels

Bots handle everything else automatically.

---

## Phase 1: The "Gatekeeper" Rules (Filtering)

### Rule 1: Newsletter Containment
**Goal:** Keep reading material out of primary inbox

**Logic:**
```
IF body contains "unsubscribe" 
AND sender is NOT in VIP list
THEN Apply Label "📰 Newsletters"
AND Skip Inbox (Archive)
```

**VIP Domains to Exclude:**
- Personal contacts
- Work domains
- Financial institutions
- Healthcare providers

**Implementation:**
- Gmail Filter OR
- `gog gmail-filter` command

---

### Rule 2: Transactional Filing
**Goal:** Archive receipts/confirmations for reference only

**Logic:**
```
IF subject or body contains:
  - "Order Confirmation"
  - "Receipt" 
  - "Invoice"
  - "Tracking Number"
  - "Payment Received"
  - "Subscription Renewal"
THEN Apply Label "📄 Paperwork/Finance"
AND Skip Inbox (Archive)
```

**Why:** These are static records. No reply needed.

---

### Rule 3: Alias Sort
**Goal:** Track who sold your data, auto-categorize

**Logic:**
```
IF delivered-to contains "+amazon"
THEN Apply Label "🛒 Shopping"

IF delivered-to contains "+social"
THEN Apply Label "📱 Social Media"

IF delivered-to contains "+work"
THEN Apply Label "💼 Work"
```

**Note:** Requires using Gmail aliases (yourname+tag@gmail.com)

---

## Phase 2: The "Janitor" Rules (Cleanup)

**Implementation:** Google Apps Script OR cron job with `gog` skill

### Rule 4: Expiration Date
**Goal:** Delete temporary emails that lost value

**Logic:**
```
IF Label is "Promotions" 
AND older_than:30d
THEN Delete

IF subject contains ("verification code" OR "one-time password" OR "security alert")
AND older_than:7d
THEN Delete
```

**Cron Schedule:** Weekly (Sunday 3am)

---

### Rule 5: Unengaged Newsletters
**Goal:** Stop hoarding unread newsletters

**Logic:**
```
IF Label is "📰 Newsletters"
AND older_than:90d
AND is:unread
THEN Delete (or Unsubscribe if possible)
```

**Cron Schedule:** Monthly (1st of month)

---

## Phase 3: The "Assistant" Rules (AI Triage)

**Implementation:** Enhance existing `gmail-monitor` cron

### Current Cron
- **Schedule:** Every 2 hours
- **Model:** DeepSeek R1
- **Task ID:** `7d9c0d86-01ff-4151-88d3-20348f1aade6`

### Enhanced Triage Prompt

**Current:**
```
📧 Check Gmail for urgent unread. Report top 3 important. Notify Eric if urgent.
```

**New (Enhanced):**
```
📧 Gmail Triage (past 2h):

1. **Urgent/Action Items:**
   - Scan unread for: questions, requests, deadlines, approvals
   - IF urgent → Notify Eric via Telegram immediately
   - IF needs review → Create Todoist task with `@eric` + `needs-eric` label

2. **Categorize Bulk:**
   - Count newsletters (don't list individually)
   - Count promotions/marketing
   - Count transactional (receipts, confirmations)

3. **Summary Format:**
   ✅ X urgent items (notified)
   📋 Y items added to Todoist for review
   📰 Z newsletters (auto-filed)
   🛒 N transactional emails (auto-filed)

4. **Only report to main session if:**
   - Found urgent items that were notified
   - Created Todoist tasks
   - Encountered errors

5. **Stay silent if:** All routine, nothing urgent
```

---

## Phase 4: Implementation Options

### Option A: Gmail Web Filters (Easiest)
1. Go to Gmail settings
2. Create filters with search criteria
3. Apply labels + skip inbox
4. **Pros:** No code, instant
5. **Cons:** Can't do time-based cleanup

### Option B: `gog` Skill (Recommended)
Use the Google Workspace CLI skill:
```bash
# Check available commands
gog gmail --help

# Create filter
gog gmail-filter create \
  --from "noreply@*.com" \
  --has "unsubscribe" \
  --label "Newsletters" \
  --skip-inbox

# Search and bulk actions
gog gmail search "label:promotions older_than:30d" --delete
```

### Option C: Google Apps Script (Most Powerful)
- Full JavaScript environment
- Time-based triggers
- Complex logic
- Can unsubscribe automatically

### Option D: Hybrid (Best)
- **Phase 1:** Gmail web filters (quick wins)
- **Phase 2:** Cron with `gog` (cleanup)
- **Phase 3:** Enhanced cron triage (AI)

---

## VIP List (Don't Auto-Archive)

These senders should ALWAYS stay in inbox:

**People:**
- Family members
- Close friends
- Direct manager/colleagues

**Domains:**
- Banks/credit cards
- Healthcare providers
- Government agencies
- Legal/tax

**Keywords to Never Archive:**
- "urgent"
- "action required"
- "security alert" (if from known sender)
- "password reset" (if from known service)

---

## Notification Rules

**Telegram Alert Criteria:**
```
IF (
  subject contains ("urgent" OR "asap" OR "deadline")
  OR from VIP sender
  OR mentions money/payment issues
  OR security alert from known service
) THEN
  Send Telegram to 6643669380
```

**Todoist Task Criteria:**
```
IF (
  appears to need response
  OR contains question directed at Eric
  OR mentions project/task
  OR unclear if important
) THEN
  Create task in Inbox with:
  - Title: "Review: [subject line]"
  - Description: Link to email + summary
  - Labels: @eric, needs-eric
  - Priority: P2
```

---

## Metrics to Track

Track in `memory/gmail-metrics.json`:

```json
{
  "lastCleanup": "2026-02-03T00:00:00Z",
  "stats": {
    "newslettersArchived": 247,
    "transactionalArchived": 89,
    "promotionsDeleted": 156,
    "urgentNotified": 12,
    "todoisTasksCreated": 8
  },
  "filters": {
    "newsletterRule": "active",
    "transactionalRule": "active",
    "cleanupCron": "active"
  }
}
```

---

## Rollout Plan

### Week 1: Foundation
- [x] Create this runbook
- [ ] Audit current Gmail inbox state
- [ ] Create VIP sender list
- [ ] Implement Phase 1 filters (newsletters + transactional)
- [ ] Test filters for 48h

### Week 2: Enhancement
- [ ] Enhance gmail-monitor cron with new triage prompt
- [ ] Test Telegram notifications
- [ ] Test Todoist task creation
- [ ] Monitor for false positives

### Week 3: Cleanup
- [ ] Implement Phase 2 cleanup cron
- [ ] Run initial cleanup (dry-run first!)
- [ ] Schedule weekly/monthly cleanup jobs

### Week 4: Optimization
- [ ] Review metrics
- [ ] Tune thresholds
- [ ] Add more filter patterns as needed
- [ ] Document learnings

---

## Testing Checklist

Before going live:

- [ ] Test newsletter filter doesn't catch VIP senders
- [ ] Test transactional filter on sample receipts
- [ ] Test urgent detection with sample emails
- [ ] Test Telegram notification delivery
- [ ] Test Todoist task creation
- [ ] Verify labels are created correctly
- [ ] Dry-run deletion (list only, don't delete)

---

## Troubleshooting

**Too many false positives:**
- Add sender to VIP list
- Refine keyword patterns
- Lower urgency threshold

**Missing important emails:**
- Check archived labels
- Expand VIP domains
- Add failsafe: "if unsure, notify"

**Cleanup too aggressive:**
- Increase time thresholds
- Add more exemptions
- Test with dry-run first

---

## Related Tasks

- Todoist: "📧 Gmail Triage System" project
- KB Article: "Gmail Automation Strategy"
- Script: `~/clawd-magi/scripts/gmail-cleanup.sh`

---

*Last Updated: 2026-02-03*
*Status: Phase 1 pending implementation*
