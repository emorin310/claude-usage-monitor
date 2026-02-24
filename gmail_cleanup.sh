#!/bin/bash
# Gmail Inbox Cleanup Script - Archives bulk/marketing emails
export GOG_ACCOUNT=emorin310@gmail.com
TOTAL=0

archive_query() {
    local label="$1"
    local query="$2"
    local count=0
    local page_token=""
    local pass=1
    
    echo "=== [$label] ==="
    
    while true; do
        if [ -z "$page_token" ]; then
            output=$(gog gmail search "$query" --max 100 --plain 2>&1)
        else
            output=$(gog gmail search "$query" --max 100 --plain --page "$page_token" 2>&1)
        fi
        
        next_page=$(echo "$output" | grep "^# Next page:" | awk '{print $NF}')
        ids=$(echo "$output" | awk 'NR>1 && /^[0-9a-f]{16}/ {print $1}')
        
        if [ -z "$ids" ]; then
            [ $count -eq 0 ] && echo "  (none found)"
            break
        fi
        
        batch_n=$(echo "$ids" | wc -l | tr -d ' ')
        echo "  Pass $pass: $batch_n messages → archiving..."
        
        # Pass all IDs at once (Gmail API handles batches)
        gog gmail batch modify --remove INBOX --force --no-input $ids 2>&1 | tail -3
        
        count=$((count + batch_n))
        pass=$((pass + 1))
        
        [ -z "$next_page" ] && break
        page_token="$next_page"
    done
    
    [ $count -gt 0 ] && echo "  ✓ $count archived"
    TOTAL=$((TOTAL + count))
    echo ""
}

echo "Gmail Cleanup → $GOG_ACCOUNT"
echo "Started: $(date)"
echo ""

# ── Explicit named senders ─────────────────────────────────────────
archive_query "AliExpress"   "in:inbox from:aliexpress"
archive_query "Craft"        "in:inbox from:craft.do"
archive_query "Blinkist"     "in:inbox from:blinkist"
archive_query "Audible"      "in:inbox from:audible"
archive_query "OLG"          "in:inbox from:olg.ca"
archive_query "Kickstarter"  "in:inbox from:kickstarter"
archive_query "VEVOR"        "in:inbox from:vevor"
archive_query "Dragonfly"    "in:inbox from:dragonfly"
archive_query "cloudHQ"      "in:inbox from:cloudhq"
archive_query "Zapier"       "in:inbox from:zapier"

# ── Political / Trump newsletters ──────────────────────────────────
archive_query "Trump (sender)"   "in:inbox from:trump"
archive_query "Trump (subject)"  "in:inbox subject:\"trump\" category:promotions"
archive_query "WinRed"           "in:inbox from:winred.com"
archive_query "GOP/NRCC"         "in:inbox from:nrcc.org"
archive_query "DonaldJTrump.com" "in:inbox from:donaldjtrump.com"

# ── Other obvious marketing that showed up in inbox scan ──────────
archive_query "Udemy marketing"  "in:inbox from:students.udemy.com"
archive_query "Udemy alerts"     "in:inbox from:e.udemymail.com"

# ── Promotions category (broad sweep, excluding protected senders) ─
# Protected: bmoalerts@bmo.com, linear*, google security, anthropic
archive_query "Promotions (general)" \
  "in:inbox category:promotions -from:bmoalerts@bmo.com -from:anthropic -from:linear.app -from:google.com"

echo "══════════════════════════════════════════"
echo "TOTAL ARCHIVED: $TOTAL"
echo "Finished: $(date)"
echo "══════════════════════════════════════════"
