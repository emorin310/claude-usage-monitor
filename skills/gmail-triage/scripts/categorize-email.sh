#!/usr/bin/env bash
set -euo pipefail

# AI Email Categorization
# Takes email JSON and returns category with confidence

EMAIL_JSON="$1"

# Extract email fields
FROM=$(echo "$EMAIL_JSON" | jq -r '.from // "Unknown"')
SUBJECT=$(echo "$EMAIL_JSON" | jq -r '.subject // "(no subject)"')
SNIPPET=$(echo "$EMAIL_JSON" | jq -r '.snippet // ""')

# Create AI prompt for categorization
PROMPT="Categorize this email into ONE of these categories:

Categories:
- Advertising (marketing, promos, sales)
- Family (personal correspondence)
- Subscriptions (newsletters, notifications)
- Receipts (purchases, invoices, orders)
- 3D Printing (MakerWorld, Thangs, Printables)
- Work/Tech (GitHub, dev tools, professional)
- Finance (banking, bills, payments)
- Events (appointments, calendar, reminders)
- Action Required (needs response/follow-up)
- Junk (spam - high confidence only)

Email:
From: $FROM
Subject: $SUBJECT
Snippet: $SNIPPET

Respond with ONLY valid JSON in this format:
{
  \"category\": \"<category name>\",
  \"confidence\": <0.0-1.0>,
  \"reason\": \"<brief explanation>\"
}"

# Call AI for categorization (placeholder - implement with actual AI call)
# For now, return a mock response
# In real implementation, this would call Claude via OpenClaw's message tool or direct API

# Simple heuristic-based categorization as fallback
CATEGORY="Subscriptions"
CONFIDENCE=0.7
REASON="Default categorization"

# Pattern matching for common senders
if echo "$FROM" | grep -qi "makerworld\|thangs\|printables"; then
  CATEGORY="3D Printing"
  CONFIDENCE=0.95
  REASON="Recognized 3D printing platform"
elif echo "$FROM" | grep -qi "github\|gitlab\|docker"; then
  CATEGORY="Work/Tech"
  CONFIDENCE=0.9
  REASON="Recognized dev platform"
elif echo "$FROM" | grep -qi "linkedin\|facebook\|twitter\|instagram"; then
  CATEGORY="Subscriptions"
  CONFIDENCE=0.85
  REASON="Social media notification"
elif echo "$FROM" | grep -qi "bank\|paypal\|stripe\|payment"; then
  CATEGORY="Finance"
  CONFIDENCE=0.9
  REASON="Financial service"
elif echo "$FROM" | grep -qi "amazon\|ebay\|aliexpress\|order\|receipt"; then
  CATEGORY="Receipts"
  CONFIDENCE=0.9
  REASON="E-commerce platform"
elif echo "$SUBJECT" | grep -qi "appointment\|meeting\|reminder\|calendar"; then
  CATEGORY="Events"
  CONFIDENCE=0.85
  REASON="Calendar-related subject"
fi

# Output JSON
jq -n \
  --arg category "$CATEGORY" \
  --arg confidence "$CONFIDENCE" \
  --arg reason "$REASON" \
  '{category: $category, confidence: ($confidence | tonumber), reason: $reason}'
