#!/usr/bin/env bash
set -euo pipefail

# Gmail Triage - Batch Processing Script
# Uses gog CLI to fetch, categorize, label, and archive emails
# Usage: ./triage-batch.sh [--batch-size 50] [--dry-run] [--account email]

BATCH_SIZE=50
DRY_RUN=false
ACCOUNT=""
TRIAGE_LABEL_PREFIX="Triage"

while [[ $# -gt 0 ]]; do
  case $1 in
    --batch-size) BATCH_SIZE="$2"; shift 2 ;;
    --dry-run)    DRY_RUN=true; shift ;;
    --account)    ACCOUNT="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Detect default account
if [[ -z "$ACCOUNT" ]]; then
  ACCOUNT=$(gog auth list --json 2>/dev/null | python3 -c "
import json,sys
accts = json.load(sys.stdin)
default = next((a for a in accts if a.get('default')), accts[0] if accts else None)
print(default['email'] if default else '')
" 2>/dev/null || echo "")
fi

echo "📧 Gmail Triage"
echo "Account: ${ACCOUNT:-default} | Batch: $BATCH_SIZE | Dry run: $DRY_RUN"
echo ""

# Ensure triage labels exist
CATEGORIES=("Advertising" "Family" "Subscriptions" "Receipts" "3D Printing" "Work/Tech" "Finance" "Events" "Action Required" "Other")
echo "🏷️  Ensuring labels exist..."
EXISTING_LABELS=$(gog gmail labels list --json ${ACCOUNT:+--account "$ACCOUNT"} 2>/dev/null | python3 -c "
import json,sys
labels = json.load(sys.stdin)
print('\n'.join(l['name'] for l in labels))
" 2>/dev/null || echo "")

for CAT in "${CATEGORIES[@]}"; do
  LABEL_NAME="${TRIAGE_LABEL_PREFIX}/${CAT}"
  if ! echo "$EXISTING_LABELS" | grep -qF "$LABEL_NAME"; then
    if [[ "$DRY_RUN" == "false" ]]; then
      gog gmail labels create "$LABEL_NAME" ${ACCOUNT:+--account "$ACCOUNT"} --no-input >/dev/null 2>&1 || true
    fi
  fi
done

# Fetch emails from inbox
echo "🔍 Fetching up to $BATCH_SIZE inbox emails..."
ACCOUNT_FLAG=""
[[ -n "$ACCOUNT" ]] && ACCOUNT_FLAG="--account $ACCOUNT"

EMAILS=$(gog gmail messages search "in:inbox" \
  $ACCOUNT_FLAG \
  --max "$BATCH_SIZE" \
  --json 2>/dev/null)

EMAIL_COUNT=$(echo "$EMAILS" | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('messages', [])))" 2>/dev/null || echo "0")
echo "Found $EMAIL_COUNT emails"

if [[ "$EMAIL_COUNT" -eq 0 ]]; then
  echo "✅ Nothing to triage!"
  exit 0
fi

# Process each email
PROCESSED=0

echo ""
echo "$EMAILS" | python3 -c "
import json,sys
data = json.load(sys.stdin)
msgs = data.get('messages', [])
for m in msgs:
    frm = m.get('from','')
    subj = m.get('subject','(no subject)')
    mid = m.get('id','')
    print(f'{mid}\t{frm[:60]}\t{subj[:80]}')
" | while IFS=$'\t' read -r MID FROM SUBJECT; do
  PROCESSED=$((PROCESSED + 1))
  echo "[$PROCESSED/$EMAIL_COUNT] $SUBJECT"
  echo "  From: $FROM"

  # Classify based on heuristics (fast, no AI cost per email)
  CATEGORY="Other"
  FROM_LOWER=$(echo "$FROM" | tr '[:upper:]' '[:lower:]')
  SUBJ_LOWER=$(echo "$SUBJECT" | tr '[:upper:]' '[:lower:]')

  if echo "$FROM_LOWER $SUBJ_LOWER" | grep -qiE "sale|promo|offer|deal|discount|unsubscribe|marketing|newsletter|aliexpress|amazon|ebay|etsy|kijiji|craigslist|doordash|skip|ubereats|grubhub|instacart"; then
    CATEGORY="Advertising"
  elif echo "$FROM_LOWER $SUBJ_LOWER" | grep -qiE "tina|mom|dad|family|brother|sister"; then
    CATEGORY="Family"
  elif echo "$FROM_LOWER $SUBJ_LOWER" | grep -qiE "makerworld|thangs|printables|bambu|prusa|thingiverse|3d print"; then
    CATEGORY="3D Printing"
  elif echo "$FROM_LOWER $SUBJ_LOWER" | grep -qiE "github|gitlab|jira|slack|linear|aws|google cloud|azure|digitalocean|cloudflare|vercel|heroku|npm|pypi|stackoverflow"; then
    CATEGORY="Work/Tech"
  elif echo "$FROM_LOWER $SUBJ_LOWER" | grep -qiE "bank|payment|invoice|receipt|order confirm|statement|bill|interac|paypal|stripe|visa|mastercard|e-transfer"; then
    CATEGORY="Finance"
  elif echo "$FROM_LOWER $SUBJ_LOWER" | grep -qiE "appointment|reminder|calendar|event|invite|rsvp|meeting|booking"; then
    CATEGORY="Events"
  elif echo "$FROM_LOWER $SUBJ_LOWER" | grep -qiE "action required|urgent|verify|confirm|your account|security alert|password"; then
    CATEGORY="Action Required"
  elif echo "$FROM_LOWER $SUBJ_LOWER" | grep -qiE "subscribe|digest|weekly|monthly|update|notification|alert"; then
    CATEGORY="Subscriptions"
  fi

  LABEL_NAME="Triage/${CATEGORY}"
  echo "  → $LABEL_NAME"

  if [[ "$DRY_RUN" == "false" ]]; then
    # Apply label + archive (remove from INBOX)
    gog gmail batch modify "$MID" \
      --add "$LABEL_NAME" \
      --remove "INBOX" \
      $ACCOUNT_FLAG \
      --no-input >/dev/null 2>&1 || echo "  ⚠️  Failed to modify $MID"
  fi
done

echo ""
echo "✅ Triage complete! ($EMAIL_COUNT emails processed)"
[[ "$DRY_RUN" == "true" ]] && echo "   (dry run — no changes made)"
