#!/bin/bash
# Send migration files to Marvin

echo "📤 Sending migration files to Marvin..."

scp ~/clawd-magi/scripts/marvin-model-migration-v2.sh marvin@marvinbot:~/
scp ~/clawd-magi/docs/marvin-migration-guide.md marvin@marvinbot:~/

ssh marvin@marvinbot 'chmod +x ~/marvin-model-migration-v2.sh'

echo "✅ Files sent! Marvin can now run:"
echo "   ./marvin-model-migration-v2.sh"
