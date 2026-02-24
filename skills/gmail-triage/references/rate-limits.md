# Gmail API Rate Limits

## Official Limits

Gmail API has these rate limits (as of 2024):

- **250 quota units per user per second**
- **1 billion quota units per day** (shared across project)

## Quota Costs

| Operation | Quota Units |
|-----------|-------------|
| List messages | 5 |
| Get message | 5 |
| Modify message (labels) | 5 |
| Send message | 100 |

## Best Practices

### Batch Processing

- Process 50-100 emails per run
- Add 0.5-1 second delay between emails
- Monitor quota usage in Google Cloud Console

### Error Handling

Handle 429 (rate limit) responses:

```bash
if [[ $STATUS -eq 429 ]]; then
  echo "Rate limited, waiting 60 seconds..."
  sleep 60
  # Retry
fi
```

### Exponential Backoff

For production usage:

```bash
RETRY_DELAY=1
MAX_RETRIES=5

for i in $(seq 1 $MAX_RETRIES); do
  if gog gmail ...; then
    break
  else
    sleep $RETRY_DELAY
    RETRY_DELAY=$((RETRY_DELAY * 2))
  fi
done
```

## Monitoring

Check quota usage:
- Google Cloud Console → APIs & Services → Dashboard
- Look for "Gmail API" usage metrics

## Daily Limits

At 50 emails/batch with 0.5s delays:
- ~7,200 emails/hour (theoretical max)
- ~100,000 emails/day (well within quota)

Safe daily target: **5,000-10,000 emails** for inbox zero projects.
