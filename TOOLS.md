
## Home Assistant

- **Skill:** `skills/homeassistant/SKILL.md`
- **Scripts:** `~/clawd-magi/skills/homeassistant/scripts/`

## Inter-Bot Communication (Magi ↔ Marvin) ⭐ NEW SYSTEM

**TL;DR:**
- **Send to Marvin:** `~/bin/msg-marvin "message"`
- **Check my inbox:** `~/bin/interbot-check`
- **Cron:** Already processing inbound messages automatically

**Details:**
- **Message directories:** `/mnt/bigstore/interbot/magi-inbox/` (TO me), `/mnt/bigstore/interbot/marvin-inbox/` (TO Marvin)
- **Processing:** Cron job (automatic, no manual checking needed)
- **Status:** ✅ Active (replaced MQTT system Feb 28, 2026 at 22:38 UTC)
- **Reliability:** Filesystem-based, no network dependencies

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