# Runbook: Scavenger Hunt (Daily Deal Hunt)

## Overview

Daily search for specific items Eric is hunting. Log findings and complete Todoist task when done.

## Schedule

| Time | Action |
|------|--------|
| 9:00 AM | Run searches, log results, mark complete |

## Hunt List

### 1. Teak Wood Furniture

**Search:** Kijiji Ontario
**Query:** "teak" OR "teak wood" in Furniture category
**Location:** Ontario (prioritize within 100km of Cambridge)

```bash
# Use web_search or web_fetch for Kijiji
web_search "site:kijiji.ca teak furniture Ontario"
```

**What to look for:**
- Outdoor teak furniture (chairs, tables, benches)
- Indoor teak pieces (shelves, cabinets)
- Reasonable pricing (under market value)
- Seller location (closer = better)

### 2. Google Coral M.2 Accelerator (AI Hardware)

**Target:** Under $60 CAD
**Item:** Google Coral M.2 Accelerator (Tensor Processing Unit)
**Key Types:**
- A+E Key (most common for WiFi slots)
- B+M Key (for NVMe slots)
- *Check Eric's specific slot need if unsure*

**Stores to check:**
- Amazon.ca
- PiShop.ca
- BuyAPi.ca
- Mouser / DigiKey (watch shipping)

```bash
web_search "Google Coral M.2 Accelerator price Canada"
```

**Why:** For Frigate/Home Assistant AI object detection (not 3D printing filament!)

## Logging Findings

## Logging Findings

### Format for Daily Notes

Add to `memory/YYYY-MM-DD.md`:

```markdown
## 🔍 Scavenger Hunt (9:00 AM)

### Teak Furniture
- **Found:** [Yes/No]
- **Listings:** [count or "none"]
- **Notable:** [any good finds with links]

### Coral TPU
- **Found:** [Yes/No]
- **Where:** [store name or "not in stock"]
- **Price:** [if found]
- **Link:** [if found]

### Action Needed
- [ ] [Any items worth alerting Eric about]
```

## Alert Criteria

**Notify Eric immediately if:**
- Teak furniture under $100 within 50km
- Coral TPU in stock under $40/kg
- Unusually good deal on either item

**Alert format (Telegram):**
```
🎯 **Scavenger Hunt Hit!**

🪵 **Teak Outdoor Chairs (Set of 4)**
💰 $150 (usually $400+)
📍 Kitchener (15 min away)
🔗 [kijiji.ca link]

Want me to save this for you?
```

## Mark Complete

After logging results:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $TODOIST_TOKEN" \
  "https://api.todoist.com/rest/v2/tasks/TASK_ID/close"
```

*Note: Replace TASK_ID with the recurring scavenger hunt task ID.*

## No Results Protocol

If nothing found:
1. Still log "No finds today" to daily notes
2. Still mark Todoist task complete
3. No alert to Eric (don't spam)

---

*Last updated: 2026-01-29*
