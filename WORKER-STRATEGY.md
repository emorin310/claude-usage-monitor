# Worker Strategy - Sub-Agent Architecture

## Overview

Instead of Magi's main session switching models (which causes session poisoning), we spawn **isolated sub-agent workers** for repetitive tasks. Each worker:
- Runs in its own session with its own model
- Completes the task and reports back
- Dies immediately (cleanup: delete)
- Cannot poison Magi's main session

**Magi stays in Sonnet forever.** Workers handle the grunt work.

## Worker Tiers (All Free Tier)

| Tier | Model(s) | Use Cases | Benefits |
|------|----------|-----------|----------|
| **1 - Sentinel** | `gemini-2.0-flash-exp` | Heartbeats, monitor checks, basic scans | Fast, cheap, high rate limits |
| **2 - Researcher** | `deepseek-r1` | Research reports, complex analysis | Better reasoning, good rate limits, free tier friendly |
| **3 - Speed Demon** | `groq/llama-3.3-70b-versatile` (pending API) | Tasks where speed matters | Sub-second response times, excellent quality |

**Cost Strategy:** Keep Sonnet ($$$) for Magi's main brain only. All workers use free-tier models to avoid burning budget on repetitive tasks.

## Active Workers

### Single-Model Workers
- **todoist-monitor** (Flash) - 9am, 12pm, 3pm, 6pm
- **council-monitor** (Flash) - 10am, 6pm
- **morning-briefing** (Flash) - 8am daily
- **afternoon-research** (DeepSeek) - 2pm daily

### Multi-Model Workers (A/B Testing)
- **gmail-monitor-multi** - Every 2 hours
  - Worker A: DeepSeek (active)
  - Worker B: Groq llama-3.3-70b (pending API key)
  - **Purpose:** Compare free-tier models on speed, accuracy, quality
  - **Note:** Sonnet removed to save costs - only free tier in rotation

## Metrics Tracking

`memory/worker-metrics.json` tracks:
```json
{
  "workers": {
    "gmail-flash": {
      "runs": 12,
      "successes": 11,
      "failures": 1,
      "avgDurationMs": 4250,
      "lastRun": "2026-02-01T18:00:00Z",
      "qualityScore": 8.5,
      "notes": "Occasionally misses context, fast execution"
    },
    "gmail-deepseek": {
      "runs": 12,
      "successes": 12,
      "failures": 0,
      "avgDurationMs": 7800,
      "lastRun": "2026-02-01T18:00:00Z",
      "qualityScore": 9.2,
      "notes": "More thorough, better reasoning, slower"
    },
    "gmail-sonnet": {
      "runs": 12,
      "successes": 12,
      "failures": 0,
      "avgDurationMs": 5100,
      "lastRun": "2026-02-01T18:00:00Z",
      "qualityScore": 9.8,
      "notes": "Best quality, balanced speed, higher cost"
    }
  },
  "comparisons": {
    "gmail": {
      "winner": "deepseek-r1",
      "reason": "Best balance of quality, speed, and rate limits",
      "confidence": "medium",
      "lastUpdated": "2026-02-01"
    }
  }
}
```

## Benefits

1. **No Session Poisoning** - Main session never switches models
2. **Parallel Execution** - Multiple workers can run simultaneously
3. **Model Optimization** - Right model for right task
4. **Rate Limit Resilience** - Failures isolated to worker sessions
5. **A/B Testing** - Empirical data on which models work best
6. **Cost Efficiency** - Use cheap models where appropriate

## Workflow

**Old (Broken):**
```
Cron → Magi switches to Flash → Executes task → Gets stuck in Flash → Session poisoned
```

**New (Fixed):**
```
Cron → Magi (stays Sonnet) → Spawns Flash worker → Worker executes → Worker reports → Worker dies → Magi synthesizes results
```

## Next Steps

1. ✅ Implement multi-worker Gmail monitoring
2. ✅ Refactor existing crons to use spawn
3. ⏳ Collect metrics over 1 week
4. ⏳ Analyze which models perform best for each task type
5. ⏳ Optimize worker assignments based on data
6. ⏳ Add more worker types (calendar, social media, deal hunting)

---

*Implemented: 2026-02-01*
*Last Updated: 2026-02-01*
