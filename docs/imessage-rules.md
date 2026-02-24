# iMessage Rules for Magi

## Overview
Magi monitors the **40Tallows** family group chat via BlueBubbles but follows strict engagement rules.

## Rules

### 1. Channel Restrictions
- ✅ **40Tallows group only** (`chat46945336443044884`)
- ❌ **No DMs** - dmPolicy is disabled
- ❌ **No other groups** - groupPolicy is allowlist

### 2. Mention-Based Activation
- **Silent by default** - `requireMention: true`
- Only respond when someone says "magi" (case-insensitive)
- When mentioned: Reply with "Magi here!" + answer the request

### 3. Activity Timeout (60 minutes)
- After being mentioned, Magi is "active" for 60 minutes
- Can respond to follow-up questions during active period
- After 60 minutes of no mentions: Send "Magi signing off" and go silent
- State tracked in: `memory/imessage-magi-state.json`

### 4. Response Style
- Keep replies brief and helpful
- Don't spam the family chat
- Be friendly but not intrusive

## State File
Location: `memory/imessage-magi-state.json`

```json
{
  "lastMentionedAt": "ISO timestamp or null",
  "isActive": true/false,
  "lastSignedOffAt": "ISO timestamp or null",
  "groupGuid": "chat46945336443044884",
  "groupName": "40Tallows"
}
```

## Cron Job
A cron job runs every 15 minutes to check if 60 minutes have passed since last mention.
If so, sends "Magi signing off" to 40Tallows and sets isActive to false.

## Config
```json
"bluebubbles": {
  "dmPolicy": "disabled",
  "groupPolicy": "allowlist",
  "groups": {
    "chat46945336443044884": {
      "requireMention": true
    }
  }
}
```
