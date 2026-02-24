# Gmail Label Management

## Creating Labels

Labels must exist before applying them to emails.

### Via gog CLI

```bash
# gog doesn't yet support label creation
# Use Gmail web interface or API directly
```

### Via Gmail Web Interface

1. Open Gmail
2. Settings → Labels
3. Create New Label
4. Enter name exactly as skill expects

### Required Labels for Skill

Create these labels in Gmail:

- `Advertising`
- `Family`
- `Subscriptions`
- `Receipts`
- `3D Printing`
- `Work/Tech`
- `Finance`
- `Events`
- `Action Required`
- `Junk`

## Label Hierarchy

Gmail supports nested labels with `/`:

```
3D Printing/MakerWorld
3D Printing/Thangs
3D Printing/Printables
```

Modify skill categories to use hierarchy if desired.

## Applying Labels via API

When gog adds label support, commands will look like:

```bash
gog gmail labels apply <message-id> "Advertising"
gog gmail labels remove <message-id> "INBOX"
```

## Current Workaround

Until gog supports labels, use Gmail API directly:

```bash
curl -X POST \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages/$MESSAGE_ID/modify" \
  -H "Authorization: Bearer $(gog auth token)" \
  -H "Content-Type: application/json" \
  -d "{
    \"addLabelIds\": [\"Label_123\"],
    \"removeLabelIds\": [\"INBOX\"]
  }"
```

Get label IDs:

```bash
curl "https://gmail.googleapis.com/gmail/v1/users/me/labels" \
  -H "Authorization: Bearer $(gog auth token)"
```

## Best Practices

- Use consistent naming (no emojis in actual labels, only in docs)
- Case-sensitive: `Advertising` ≠ `advertising`
- Test label application on 1-2 emails first
- Verify labels appear in Gmail web interface
