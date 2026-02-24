# Activity Journal

## 2026-02-02

### Alert: Extended Downtime (5:00 PM - 9:30 PM)
- **Type:** Alert
- **Duration:** ~4.5 hours
- **Detected by:** Marvin's monitoring system (12 sequential alerts)
- **Cause:** Unknown (likely system restart or gateway crash)
- **Recovery:** Back online at 9:40 PM, all systems operational
- **Action:** Posted recovery status to Council

### Task: Model Override Bug Investigation
- **Type:** Task
- **Issue:** Discovered critical bug in worker/subagent model selection
- **Finding:** Workers spawned with `model="llama-8b"` or `model="deepseek-r1"` fall back to Opus
- **Root Cause:** Aggressive fallback chain in agent config - any minor issue triggers fallback
- **Impact:** DeepSeek workers showing 0K usage because they're actually using Opus
- **Evidence:** Test worker requested llama-8b, actually used claude-opus-4-5
- **Status:** Bug identified, solution proposed (disable fallbacks for free models)
- **Next:** Pending Eric's approval to apply config patch

### Event: Model Testing Request
- **Type:** Event
- **Request:** Eric wants to test Llama and DeepSeek models for different worker tasks
- **Goal:** Compare performance and effectiveness vs Claude
- **Approach:** Spawn workers with various models doing similar tasks
- **Blocked by:** Model override bug (workers not using requested models)

### Task: New Model Additions
- **Type:** Task
- **Added:** Kimi K2.5 (Moonshot AI) for brain/content writing tasks
- **Added:** Haiku (Anthropic) for fast heartbeat checks
- **API Key:** Received and configured for Kimi
- **Status:** Both models configured with aliases (`kimi`, `haiku`)
- **Pending:** Minimax 2.1, ChatGPT 4o Realtime, DeepSeek V3 clarification

### Project: OpenClaw Migration Planning
- **Type:** Project
- **Discovery:** Running old clawdbot 2026.1.24-3, latest is OpenClaw 2026.2.1
- **Issue:** Likely source of model limitations and config restrictions
- **Action:** Spawned Opus worker to create comprehensive migration plan
- **Deliverable:** Complete runbook at ~/clawd-magi/runbooks/openclaw-migration.md (865 lines)
- **Risk Assessment:** LOW - automatic migration, backwards compatible
- **Status:** Plan complete, ready for Eric's review and execution
- **Link:** https://app.todoist.com/app/task/[pending]

### Event: Marvin OpenClaw Migration (COMPLETE)
- **Type:** Event
- **Date:** 2026-02-02 23:01-23:07 EST
- **Duration:** ~6 minutes
- **From:** moltbot 2026.1.29 (git source)
- **To:** OpenClaw 2026.2.1
- **Backup:** VM snapshot + file-level backups at ~/backups/pre-openclaw-20260202-230146
- **Phases Completed:**
  1. ✅ Pre-flight checks (pnpm installed)
  2. ✅ Pre-migration backups
  3. ✅ Services stopped
  4. ✅ Git remote migrated (clawdbot → openclaw)
  5. ✅ Built from source (pnpm install + build + ui:build)
  6. ✅ Config migrated (doctor auto-migration)
  7. ✅ Systemd service updated and started
  8. ⏭️ Cron jobs (skipped, will review later)
  9. ✅ Post-migration validation (all tests passed)
- **Result:** SUCCESS - Marvin fully operational on OpenClaw 2026.2.1
- **Gateway:** ws://0.0.0.0:18789, active and responding
- **Telegram:** Test message sent successfully (message ID: 1062)
- **Next:** Magi migration (when Eric is ready)

### Task: Marvin Model Switch to Opus
- **Type:** Task
- **Time:** 2026-02-02 23:29 EST
- **Action:** Changed Marvin's default model from phi4:latest to claude-opus-4-5
- **Method:** Updated openclaw.json, restarted gateway
- **Status:** Complete, gateway active
