# Credit & Model Strategy

**Goal:** Maximize intelligence per credit by routing tasks to the most efficient effective model.

## The 3-Tier Model Architecture

We organize model usage into three distinct tiers based on cost, capability, and latency.

| Tier | Role | Primary Models | Cost Profile |
|------|------|----------------|--------------|
| **1** | **Architect (Reasoning)** | **Claude 3 Opus**, **Claude 3.5 Sonnet** (High-Load) | High |
| **2** | **Agent (Daily Driver)** | **Claude 3.5 Sonnet**, **Gemini 1.5 Pro** | Medium |
| **3** | **Sentinel (Fast/Free)** | **Gemini 2.0 Flash**, **Gemini 1.5 Flash** | Low/Free |

---

## Tier Definitions & Use Cases

### 🧠 Tier 1: The Architect (Deep Reasoning)
**When to use:** Complex problem solving, strategic planning, creative writing, nuanced human interaction.
**Threshold:** Use when session context is critical or task failure has high consequences.

*   **System Architecture:** Designing multi-agent systems, complex runbooks (e.g., `model-tier-management.md`).
*   **Deep Research:** Synthesizing disparate sources (e.g., "Find best approach to X with constraints Y and Z").
*   **Coding:** Refactoring complex logic, debugging race conditions.
*   **Emotional/Personal:** Drafting sensitive messages, complex family planning (`user-family.md` context).

### 🛠️ Tier 2: The Agent (Daily Operations)
**When to use:** Standard tasks, content processing, structured data manipulation.
**Threshold:** Default for most user-facing tasks not requiring "deep thought."

*   **Content Curation:** Summarizing news for Morning Briefing (`morning-briefing-prep`).
*   **Task Management:** Organizing Todoist projects, parsing natural language into tasks.
*   **Shopping/Deal Hunting:** evaluating products against criteria (`user-interests.md` - e.g., "Is this Teak wood genuine?").
*   **Drafting:** Writing routine emails, journal entries (`journal-system.md`).

### ⚡ Tier 3: The Sentinel (Monitoring & Speed)
**When to use:** High-frequency checks, simple lookups, summarizing short text, filtering noise.
**Threshold:** Always use for background jobs, heartbeats, and "is this interesting?" filters.

*   **Heartbeats:** Checking email/calendar/notifications (`HEARTBEAT.md`).
*   **Web Scraping:** Extracting specific fields from web pages (e.g., checking price of Coral TPU).
*   **Log Analysis:** Scanning logs for errors (e.g., `failsafe.log` analysis).
*   **Weather/Status:** Fetching and formatting simple data APIs.

---

## Operational Rules

### 1. Quota Awareness
- **Green (0-50%):** Tier 1 allowed for all "Architect" tasks.
- **Yellow (50-75%):** Tier 1 restricted to *critical* paths. Move "Drafting" to Tier 2.
- **Red (>90%):** Tier 3 ONLY. Sub-agents must use Tier 3.

### 2. Sub-Agent Delegation
Spawn sub-agents to offload context and processing.
- **Research:** "Search the web for X and summarize" -> Tier 2 Sub-agent.
- **Bulk Edit:** "Update all 50 tasks in Todoist" -> Tier 3 Sub-agent.

### 3. Failsafe
If Tier 1/2 hit rate limits or quotas, system automatically falls back to **Gemini 2.0 Flash** (Tier 3) to maintain uptime.

---

*Last Updated: 2026-02-03*
