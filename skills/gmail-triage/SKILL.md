---
name: gmail-triage
description: AI-driven Gmail inbox management for achieving inbox zero through intelligent email categorization, labeling, archiving, and task extraction. Use when managing Gmail inbox cleanup, triaging large backlogs, applying labels to emails, extracting actionable items from emails, or automating inbox organization workflows.
---

# Gmail Triage

Intelligent Gmail inbox management using AI categorization, automated labeling, and task extraction.

## Prerequisites

- `gog` CLI installed and authenticated (`gog auth list` to verify)
- Gmail account configured with necessary permissions

## Quick Start

Process 50 oldest emails with AI categorization:

```bash
scripts/triage-batch.sh --batch-size 50
```

View current inbox status:

```bash
gog gmail messages search "in:inbox" --max 1 --json | jq '.[0]'
```

## Categories

The skill uses AI to automatically categorize emails into these labels:

- **📣 Advertising** - Marketing, promos, sales emails
- **👨‍👩‍👧‍👦 Family** - Personal correspondence from family/friends
- **🔔 Subscriptions** - Newsletters, automated notifications
- **🧾 Receipts** - Purchase confirmations, invoices, order updates
- **🏗️ 3D Printing** - MakerWorld, Thangs, Printables notifications
- **💼 Work/Tech** - GitHub, dev tools, professional services
- **🏦 Finance** - Banking, bills, payment notices
- **📅 Events** - Appointments, calendar invitations, reminders
- **🎯 Action Required** - Emails needing response or follow-up
- **🗑️ Junk** - Spam (use cautiously, requires high confidence)

## Workflow

1. Fetch oldest N emails from inbox
2. For each email:
   - AI analyzes sender, subject, snippet
   - Assigns appropriate label(s)
   - Archives the email
   - Extracts actionable items (if any)
3. Creates Todoist tasks for action items
4. Reports progress via Telegram

## Scripts

### `scripts/triage-batch.sh`

Main batch processing script.

**Usage:**
```bash
scripts/triage-batch.sh [OPTIONS]

Options:
  --batch-size N     Process N emails (default: 50)
  --dry-run          Show what would happen without making changes
  --account EMAIL    Gmail account to use (default: from gog auth)
  --state-file PATH  State persistence file (default: ~/.gmail-triage-state.json)
```

**Example:**
```bash
# Process 100 emails in dry-run mode
scripts/triage-batch.sh --batch-size 100 --dry-run

# Process 50 emails for specific account
scripts/triage-batch.sh --account emorin310@gmail.com
```

### `scripts/categorize-email.sh`

AI categorization for a single email (called by triage-batch.sh).

**Usage:**
```bash
scripts/categorize-email.sh <email-json>
```

Returns JSON with category and confidence.

## State Management

Progress tracked in `~/.gmail-triage-state.json`:

```json
{
  "lastProcessedId": "abc123",
  "lastRunAt": "2026-02-15T12:00:00Z",
  "stats": {
    "totalProcessed": 500,
    "byCategory": {
      "Advertising": 150,
      "Subscriptions": 100,
      "Family": 50
    }
  }
}
```

## Advanced Usage

### Scheduled Processing

Run via cron for continuous inbox management:

```json
{
  "name": "Gmail Triage - Daily",
  "schedule": { "kind": "cron", "expr": "0 2 * * *", "tz": "America/Toronto" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run gmail-triage skill to process 100 oldest emails. Report summary to Telegram."
  },
  "sessionTarget": "isolated"
}
```

### Todoist Integration

Action items automatically create tasks in Todoist:

- **Appointments** → Calendar tasks with due dates
- **Action Required** → Tasks with `@needs-eric` label
- **Follow-ups** → Tasks with appropriate context

## Troubleshooting

**No emails returned:**
- Check query: `gog gmail messages search "in:inbox" --max 5`
- Verify account: `gog auth list`

**Rate limiting:**
- Reduce `--batch-size`
- Add delays in script (see `references/rate-limits.md`)

**Label not found:**
- Gmail labels are case-sensitive
- Create labels first: `gog gmail labels create "3D Printing"`

## References

- **[rate-limits.md](references/rate-limits.md)** - Gmail API rate limit guidance
- **[label-guide.md](references/label-guide.md)** - Gmail label management patterns
- **[categorization-examples.md](references/categorization-examples.md)** - AI categorization examples for training
