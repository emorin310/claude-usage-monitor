#!/bin/bash
# check-agentmail.sh - Fetch unread messages from magi-homelab@agentmail.to
# Outputs sanitized JSON array of unread message summaries (no body content)

AGENTMAIL_TOKEN="am_us_9e22b07803c4732cada544b3db29f92c4ee4e13d804e77d6d1fdcc09fd43601e"
INBOX="magi-homelab@agentmail.to"
API_URL="https://api.agentmail.to/v0"

curl -s \
  -H "Authorization: Bearer ${AGENTMAIL_TOKEN}" \
  "${API_URL}/inboxes/${INBOX}/messages" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
messages = data.get('messages', [])
unread = [
    {
        'message_id': m['message_id'],
        'thread_id': m['thread_id'],
        'from': m.get('from', ''),
        'subject': m.get('subject', '')[:120],
        'preview': m.get('preview', '')[:200],
        'timestamp': m.get('timestamp', ''),
        'labels': m.get('labels', [])
    }
    for m in messages
    if 'unread' in m.get('labels', [])
]
print(json.dumps({'count': len(unread), 'messages': unread}))
"
