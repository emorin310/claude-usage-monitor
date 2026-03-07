
## Home Assistant

- **Skill:** `skills/homeassistant/SKILL.md`
- **Scripts:** `~/clawd-magi/skills/homeassistant/scripts/`

## Multi-Agent Communication (Deprecated)

**⚠️ DEPRECATED:** Interbot messaging system has been retired as of March 7, 2026.
- **Replaced by:** Marvin Jr. subagent system via OpenClaw sessions_spawn
- **Old scripts:** Archived to `~/clawd/archive/interbot-deprecated/`
- **Media requests:** Now handled via sessions_send to marvin-jr agent
- **Status:** ❌ Decommissioned (scripts archived, cron jobs removed)

## Excalidraw Flowchart

- **Source:** https://playbooks.com/skills/openclaw/skills/excalidraw-flowchart
- **Repo:** https://github.com/swiftlysingh/excalidraw-skill
- **Usage:** Create flowcharts and diagrams from descriptions
- **Command:** `npx @swiftlysingh/excalidraw-cli create --inline "<DSL>" -o flowchart.excalidraw`
- **Formats:** DSL (custom syntax), DOT/Graphviz, JSON
- **Use when:** User asks to "create a flowchart", "draw a diagram", "visualize a process", "architecture diagram"
- **DSL Elements:**
  - `[Label]` = Rectangle (process step)
  - `{Label?}` = Diamond (decision)
  - `(Label)` = Ellipse (start/end)
  - `[[Label]]` = Database
  - `->` = Arrow (connection)
  - `-->` = Dashed arrow (optional path)

## Draw.io Diagrams

- **Location:** `/mnt/bigstore/knowledge/shared/drawio/`
- **Skill:** Professional draw.io diagram creation and editing
- **Usage:** Create architecture diagrams, flowcharts, AWS diagrams with professional styling
- **Key Capabilities:**
  - Direct XML editing of `.drawio` files
  - Automated PNG conversion (2x resolution, transparent background)
  - Programmatic layout adjustment and alignment
  - AWS icon integration (official icons, latest versions)
  - Design principles enforcement (clarity, consistency, accessibility)
  - Quality assurance checklist
- **Convert to PNG:**
  ```bash
  bash ~/.claude/skills/draw-io/scripts/convert-drawio-to-png.sh diagram.drawio
  ```
- **Find AWS Icons:**
  ```bash
  python ~/.claude/skills/draw-io/scripts/find_aws_icon.py ec2
  ```
- **Use when:** Need professional architecture diagrams, AWS diagrams, or complex technical visuals
- **Output:** `.drawio.png` high-resolution images (transparent, presentation-ready)
- **Best for:** Architecture diagrams, system designs, AWS infrastructure, technical documentation
## New Skills (March 7, 2026)

### 🎮 GOG (Google Workspace CLI)
- **Location:** `~/clawd/skills/gog/`
- **Purpose:** Google Workspace management (Gmail, Calendar, Drive, Contacts, Sheets, Docs)
- **Agent:** Beeb (Ops-Scout)
- **Commands:**
  - Gmail search: `gog gmail search 'newer_than:7d' --max 10`
  - Gmail send: `gog gmail send --to a@b.com --subject "Hi" --body "Hello"`
  - Calendar: `gog calendar events <calendarId> --from <iso> --to <iso>`
- **Setup:** Requires OAuth setup with Google credentials

### 📧 Gmail Secretary  
- **Location:** `~/clawd/skills/gmail-secretary/`
- **Purpose:** Gmail triage assistant using Haiku LLM for classification and draft replies
- **Agent:** Beeb (Ops-Scout)
- **Safety:** Never auto-sends emails, only creates drafts and summaries
- **Features:** Email labeling, urgency classification, draft generation

### 🧠 Self-Improving Agent
- **Location:** `~/clawd/skills/self-improving/`  
- **Purpose:** Proactive self-reflection, self-criticism, and learning system
- **Agent:** Magi (Orchestrator)
- **Features:** 
  - Structured memory system in `~/self-improving/`
  - Hot memory (≤100 lines), domain-specific learning, project learnings
  - Self-evaluation and mistake catching
  - Knowledge compounding over time

### 🚀 Agent Autonomy Kit
- **Location:** `~/clawd/skills/agent-autonomy-kit/`
- **Purpose:** Transform agents from reactive to proactive with task queues
- **Agent:** All agents
- **Features:**
  - Task queue management (Ready/In Progress/Blocked/Done)
  - Autonomous work patterns without prompting

### 💻 Development Skills (Deap Agent) ⭐ NEW
**Agent:** Deap (Deep Thought) - Lead Developer & GitHub Repository Manager  
**Installed:** March 7, 2026  
**Purpose:** Specialized development agent to handle all coding tasks and free Magi for orchestration

#### **git** - Comprehensive GitHub Management
- **Location:** `~/clawd/skills/git/`
- **Capabilities:** Full version control, branching strategies, team workflows, recovery techniques
- **Usage:** All Git operations, GitHub workflows, repository management

#### **explain-code** - Code Analysis & Explanations  
- **Location:** `~/clawd/skills/explain-code/`
- **Capabilities:** Code analysis, explanation generation, debugging assistance
- **Usage:** Code reviews, documentation, debugging support

#### **documentation** - Automated Documentation Generation
- **Location:** `~/clawd/skills/documentation/`
- **Capabilities:** API docs, technical guides, automated documentation
- **Usage:** Generate comprehensive documentation for projects

#### **test-runner** - Multi-Language Testing
- **Location:** `~/clawd/skills/test-runner/`
- **Capabilities:** Vitest/Jest (JS/TS), pytest (Python), XCTest (Swift), Playwright (E2E)
- **Usage:** Automated testing across multiple languages and frameworks

### 🎯 Development Workflow:
1. **Magi delegates coding tasks** to Deap via sessions_spawn
2. **Deap uses specialized skills** for development work  
3. **Deap commits to GitHub** with proper documentation
4. **Deap reports completion** back to Magi
  - Cron job integration for overnight work
  - Daily reporting automation

