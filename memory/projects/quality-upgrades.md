# Quality Upgrades Project

## Status: AUTOMATED & ACTIVE ✅
**Started:** 2026-03-01T04:47:00Z
**Automation enabled:** 2026-03-01T15:53:00Z
**Target:** Complete library quality improvement - continuous processing until all media meets minimum standards

## Approach:
- **Rate limit:** 1 upgrade per day (steady, continuous progress)
- **Target quality:** 1080p minimum, modern codecs (x264/x265/AV1)
- **Containers:** Prefer MKV/MP4 over AVI
- **Tracking:** SQLite database for structured queuing
- **Automation:** Cron-based processing with Marvin coordination

## Progress:
- ✅ Database schema created and migrated
- ✅ Processing pipeline implemented and tested
- ✅ Cron automation deployed (2x daily at 15:00 & 23:00 UTC)
- ✅ Daily briefing integration (status in health checks)
- ✅ Rate limiting and state tracking active

## Current Queue:
- **5 movies queued** (4 HIGH priority, 1 LOW priority)  
- **Next target:** "While You Were Sleeping" (1995) - 288p → 1080p+
- **Processing schedule:** Daily at 15:00 UTC (10 AM EST) and 23:00 UTC (6 PM EST)

## Long-term Plan:
- **Total identified:** 589 movies flagged for quality improvement
- **Processing rate:** 1 movie per day (steady, continuous)
- **Estimated completion:** ~19 months for all flagged movies
- **Queue expansion:** Will add more movies as current queue completes
- **Success criteria:** All movies meet 1080p+ modern codec standards

## Monitoring:
- **Logs:** `logs/quality-upgrades.log`
- **Status:** Included in 30-min health check briefings
- **State file:** `memory/quality-upgrade-state.json`

*See: memory/database/memory.db → quality_queue table*
